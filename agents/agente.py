"""
Agente BI Agéntico — punto de entrada principal.

Expone responder(pregunta) -> dict con:
  {"respuesta": str, "herramientas_usadas": [{"nombre", "argumentos", "resultado"}]}

Flujo:
  1. Abre cliente MCP (stdio) y lista las herramientas disponibles.
  2. Convierte cada herramienta en una FunctionDeclaration de Gemini.
  3. Bucle de hasta 5 vueltas: LLM → llama herramienta → devuelve resultado → repite.
  4. Respuesta final en español, solo con datos reales de las herramientas.
  5. Guarda evidencia en logs/agente.log.
"""
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ── Configuración ──────────────────────────────────────────────────────────────

RAIZ = Path(__file__).resolve().parent.parent
# Ruta absoluta al .env: funciona aunque se lance desde otra carpeta (Streamlit)
load_dotenv(RAIZ / ".env")
LLM_API_KEY = os.getenv("LLM_API_KEY")
# Modelo configurable desde .env (LLM_MODEL); por defecto gemini-2.5-flash
MODELO = os.getenv("LLM_MODEL", "gemini-2.5-flash")

# Cambia a True para usar el servidor real (requiere Supabase).
# False → usa tests/mcp_falso.py para desarrollo.
USAR_SERVIDOR_REAL = True

if USAR_SERVIDOR_REAL:
    SCRIPT_MCP = str(RAIZ / "backend" / "mcp_server.py")
else:
    SCRIPT_MCP = str(RAIZ / "tests" / "mcp_falso.py")

MAX_VUELTAS = 5  # máximo de iteraciones herramienta → LLM

# ── Logging ────────────────────────────────────────────────────────────────────

logs_dir = RAIZ / "logs"
logs_dir.mkdir(exist_ok=True)

logging.basicConfig(
    filename=str(logs_dir / "agente.log"),
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    encoding="utf-8",
)


def _log(pregunta: str, herramientas: list, respuesta: str) -> None:
    """Guarda pregunta, herramientas usadas y respuesta en el log."""
    logging.info("PREGUNTA: %s", pregunta)
    for h in herramientas:
        logging.info(
            "  HERRAMIENTA: %s | args=%s | resultado=%s",
            h["nombre"],
            h["argumentos"],
            str(h["resultado"])[:300],
        )
    logging.info("RESPUESTA: %s", respuesta[:500])
    logging.info("-" * 60)


# ── Instrucciones del sistema ──────────────────────────────────────────────────

def _cargar_system_prompt() -> str:
    """Lee AGENTS.md y SKILL.md para construir el system prompt."""
    agents_md = (RAIZ / "AGENTS.md").read_text(encoding="utf-8")
    skill_md = (RAIZ / "skills" / "analisis-reposicion" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    return (
        f"{agents_md}\n\n{skill_md}\n\n"
        "Responde SIEMPRE en español. "
        "Usa SOLO números que provengan de las herramientas MCP. "
        "Si una herramienta devuelve error, indícalo claramente en lugar de inventar datos."
    )


# ── Conversión de esquema MCP → Gemini ────────────────────────────────────────

def _limpiar_schema(obj: dict) -> dict:
    """Elimina campos que Gemini no acepta en los esquemas JSON."""
    campos_prohibidos = {"title", "additionalProperties", "default", "$schema"}
    if not isinstance(obj, dict):
        return obj
    limpio = {}
    for k, v in obj.items():
        if k in campos_prohibidos:
            continue
        if isinstance(v, dict):
            limpio[k] = _limpiar_schema(v)
        elif isinstance(v, list):
            limpio[k] = [_limpiar_schema(i) if isinstance(i, dict) else i for i in v]
        else:
            limpio[k] = v
    return limpio


def _mcp_a_gemini(herramienta) -> types.Tool:
    """Convierte una herramienta MCP en un Tool de Gemini."""
    schema_raw = {}
    if herramienta.input_schema:
        schema_raw = (
            herramienta.input_schema
            if isinstance(herramienta.input_schema, dict)
            else herramienta.input_schema.model_dump()
        )
    schema = _limpiar_schema(schema_raw)
    # Gemini necesita que 'properties' exista aunque la herramienta no tenga params
    if "properties" not in schema:
        schema["properties"] = {}
    # Quitar required si viene vacío
    if "required" in schema and not schema["required"]:
        del schema["required"]

    declaracion = types.FunctionDeclaration(
        name=herramienta.name,
        description=herramienta.description or "",
        parameters=schema if schema.get("properties") else None,
    )
    return types.Tool(function_declarations=[declaracion])


def _leer_resultado(resultado):
    """Convierte la respuesta de una herramienta MCP en dict/lista de Python.
    Primero usa el contenido estructurado; si no hay, une todos los bloques de texto
    (una lista puede llegar como varios bloques, uno por elemento)."""
    estructurado = getattr(resultado, "structuredContent", None) or getattr(
        resultado, "structured_content", None
    )
    if estructurado is not None:
        # FastMCP envuelve las listas como {"result": [...]}
        if isinstance(estructurado, dict) and list(estructurado.keys()) == ["result"]:
            return estructurado["result"]
        return estructurado
    valores = []
    for bloque in resultado.content or []:
        texto = getattr(bloque, "text", None)
        if texto is None:
            continue
        try:
            valores.append(json.loads(texto))
        except json.JSONDecodeError:
            valores.append(texto)
    if len(valores) == 1:
        return valores[0]
    return valores


# ── Núcleo async ───────────────────────────────────────────────────────────────

async def _responder_async(pregunta: str) -> dict:
    """Lógica principal: cliente MCP + bucle Gemini."""

    system_prompt = _cargar_system_prompt()
    python_exe = sys.executable  # misma versión de Python / .venv

    params = StdioServerParameters(
        command=python_exe,
        args=[SCRIPT_MCP],
        env=dict(os.environ),  # pasa el entorno completo (con env=None el SDK solo pasa PATH y poco más)
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. Listar herramientas del servidor MCP
            lista = await session.list_tools()
            herramientas_mcp = lista.tools

            # Construir tools para Gemini (una Tool con todas las declaraciones)
            declaraciones = []
            for h in herramientas_mcp:
                tool_gemini = _mcp_a_gemini(h)
                declaraciones.extend(tool_gemini.function_declarations)
            tools_gemini = [types.Tool(function_declarations=declaraciones)]

            # 2. Inicializar cliente Gemini
            cliente = genai.Client(api_key=LLM_API_KEY)
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                tools=tools_gemini,
            )

            # Historial de mensajes para el bucle
            mensajes = [types.Content(role="user", parts=[types.Part(text=pregunta)])]
            herramientas_usadas = []

            # 3. Bucle herramienta → LLM (máximo MAX_VUELTAS)
            for _ in range(MAX_VUELTAS):
                respuesta = await asyncio.to_thread(
                    cliente.models.generate_content,
                    model=MODELO,
                    contents=mensajes,
                    config=config,
                )

                candidato = respuesta.candidates[0]
                if candidato.content is None or not candidato.content.parts:
                    break  # respuesta vacía o bloqueada: salimos del bucle
                mensajes.append(candidato.content)  # añadir respuesta al historial

                # ¿El modelo pide llamar alguna herramienta?
                llamadas = [
                    p.function_call
                    for p in candidato.content.parts
                    if p.function_call is not None
                ]
                if not llamadas:
                    break  # el modelo ya dio respuesta final

                # Ejecutar cada herramienta en el servidor MCP
                resultados_parts = []
                for fc in llamadas:
                    args = dict(fc.args) if fc.args else {}
                    resultado = await session.call_tool(fc.name, args)
                    valor = _leer_resultado(resultado)

                    herramientas_usadas.append(
                        {"nombre": fc.name, "argumentos": args, "resultado": valor}
                    )

                    resultados_parts.append(
                        types.Part(
                            function_response=types.FunctionResponse(
                                name=fc.name,
                                response={"result": valor},
                            )
                        )
                    )

                # Devolver resultados al LLM
                mensajes.append(
                    types.Content(role="user", parts=resultados_parts)
                )

            # 4. Extraer texto final
            texto_final = ""
            if candidato.content and candidato.content.parts:
                for part in candidato.content.parts:
                    if getattr(part, "text", None):
                        texto_final += part.text
            if not texto_final.strip():
                texto_final = ("No he podido generar una respuesta completa. "
                               "Revisa en 'Cómo lo ha calculado' los datos obtenidos.")

            _log(pregunta, herramientas_usadas, texto_final)

            return {
                "respuesta": texto_final.strip(),
                "herramientas_usadas": herramientas_usadas,
            }


# ── API pública (síncrona, apta para Streamlit) ────────────────────────────────

def responder(pregunta: str) -> dict:
    """
    Responde una pregunta de negocio usando herramientas MCP y Gemini.

    Args:
        pregunta: Pregunta en lenguaje natural sobre ventas retail.

    Returns:
        {"respuesta": str, "herramientas_usadas": list[dict]}
    """
    return asyncio.run(_responder_async(pregunta))


# ── Prueba rápida ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pregunta = "¿Qué productos importantes están cayendo?"
    print(f"\nPregunta: {pregunta}\n")
    resultado = responder(pregunta)
    print("=== RESPUESTA ===")
    print(resultado["respuesta"])
    print("\n=== HERRAMIENTAS USADAS ===")
    for h in resultado["herramientas_usadas"]:
        print(f"  • {h['nombre']}({h['argumentos']})")

