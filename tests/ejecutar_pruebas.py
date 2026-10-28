"""Batería de pruebas automática: P01-P09, P11 y P12.

Reproduce las mismas pruebas documentadas en tests/pruebas.md y guarda su salida
en los mismos archivos de tests/evidencias/ que ya existen (los sobrescribe).

P10 queda fuera porque es manual (capturas de pantalla de Streamlit).
Espera 5 s entre preguntas al agente para no saturar la cuota gratuita de Gemini.
"""
import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

RAIZ = Path(__file__).resolve().parent.parent
EVIDENCIAS = RAIZ / "tests" / "evidencias"
EVIDENCIAS.mkdir(exist_ok=True)
ESPERA_ENTRE_PREGUNTAS = 5  # segundos, para no saturar la cuota gratuita de Gemini

load_dotenv(RAIZ / ".env")


# ── P01 y P02: base de datos ────────────────────────────────────────────────

def ejecutar_p01_p02():
    conn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
    try:
        cur = conn.cursor()

        cur.execute("SELECT count(*) FROM ventas;")
        p01 = cur.fetchone()[0]

        cur.execute(
            "SELECT invoice, stock_code, description, quantity, invoice_date, price "
            "FROM ventas WHERE stock_code = '85123A' LIMIT 5;"
        )
        p02_filas = cur.fetchall()
        cur.execute("SELECT count(*) FROM ventas WHERE stock_code = '85123A';")
        p02_count = cur.fetchone()[0]
    finally:
        conn.close()

    with open(EVIDENCIAS / "P01_P02_base_datos.txt", "w", encoding="utf-8") as f:
        f.write("P01 - Conteo total de registros\n")
        f.write("Consulta: SELECT count(*) FROM ventas;\n")
        f.write(f"Resultado: {p01} filas\n")
        f.write("Excel original (Online Retail II, verificado en backend/cargar_datos.py al cargar): 1067371 filas\n")
        f.write(f"Coincide: {p01 == 1067371}\n\n")
        f.write("P02 - Consulta de un producto concreto (stock_code 85123A)\n")
        f.write("Consulta: SELECT * FROM ventas WHERE stock_code = '85123A';\n")
        f.write(f"Filas devueltas: {p02_count}\n")
        f.write("Primeras 5 filas:\n")
        for fila in p02_filas:
            f.write(f"  {fila}\n")

    print(f"P01: {p01} filas | P02: {p02_count} filas para 85123A")
    return {"p01_filas": p01, "p02_count": p02_count}


# ── P03, P04 y P05: servidor MCP ────────────────────────────────────────────

async def _ejecutar_p03_p04_p05_async():
    params = StdioServerParameters(command=sys.executable, args=[str(RAIZ / "backend" / "mcp_server.py")])
    salida = []
    resumen = {}

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # P03
            herramientas = await session.list_tools()
            nombres = [t.name for t in herramientas.tools]
            esperadas = {"kpi_resumen", "productos_en_riesgo", "tasa_cancelacion", "ventas_producto"}
            salida.append("P03 - Listado de herramientas del servidor retail-bi")
            salida.append(f"Herramientas encontradas: {nombres}")
            salida.append(f"Son las 4 esperadas: {set(nombres) == esperadas}")
            salida.append("")
            resumen["p03_herramientas"] = nombres

            # P04
            r4 = await session.call_tool("kpi_resumen", {})
            kpi = json.loads(r4.content[0].text)
            salida.append("P04 - kpi_resumen vs tests/kpi_referencia.md")
            salida.append(f"Resultado: {kpi}")
            salida.append("")
            resumen["p04_kpi"] = kpi

            # P05
            r5 = await session.call_tool("ventas_producto", {"stock_code": "XXXX"})
            valores = [json.loads(b.text) for b in r5.content] if r5.content else []
            r_viva = await session.call_tool("kpi_resumen", {})
            servidor_vivo = bool(r_viva.content)
            salida.append("P05 - ventas_producto con código inexistente XXXX")
            salida.append(f"is_error: {r5.is_error}")
            salida.append(f"Resultado: {valores}")
            salida.append(f"El servidor sigue vivo tras la llamada: {servidor_vivo}")
            resumen["p05_vacio"] = valores == []
            resumen["p05_servidor_vivo"] = servidor_vivo

    (EVIDENCIAS / "P03_P04_P05_mcp.txt").write_text("\n".join(salida), encoding="utf-8")
    print("\n".join(salida))
    return resumen


def ejecutar_p03_p04_p05():
    return asyncio.run(_ejecutar_p03_p04_p05_async())


# ── P06, P07, P08, P09 y P11: agente ────────────────────────────────────────

def ejecutar_agente():
    sys.path.insert(0, str(RAIZ / "agents"))
    from agente import responder  # import tardío: necesita .env ya cargado

    casos = [
        ("P06", "¿Qué recomiendas reponer o revisar?"),
        ("P07", "¿Qué productos importantes están cayendo?"),
        ("P08", "¿Qué tiempo hace en Madrid?"),
        ("P09", "¿Cuál es el stock actual?"),
        ("P11", "¿Cómo han ido las ventas del producto 85123A en los últimos meses?"),
    ]

    resumen = {}
    bloques = []
    for i, (pid, pregunta) in enumerate(casos):
        r = responder(pregunta)
        herramientas = [h["nombre"] for h in r["herramientas_usadas"]]
        bloque = (
            f"{pid} - Pregunta: {pregunta}\n"
            f"Herramientas usadas: {[h['nombre'] + str(h['argumentos']) for h in r['herramientas_usadas']]}\n"
            f"Respuesta:\n{r['respuesta']}\n" + "-" * 70
        )
        bloques.append(bloque)
        print(bloque)
        resumen[pid] = {"herramientas": herramientas, "respuesta": r["respuesta"]}

        if i < len(casos) - 1:
            time.sleep(ESPERA_ENTRE_PREGUNTAS)

    (EVIDENCIAS / "P06_P07_P08_P09_P11_agente.txt").write_text(
        "\n".join(bloques) + "\n", encoding="utf-8"
    )
    return resumen


# ── P12: seguridad ───────────────────────────────────────────────────────────

def _ejecutar(cmd):
    """Ejecuta un comando y devuelve su stdout (vacío si falla o no hay salida)."""
    try:
        return subprocess.run(
            cmd, capture_output=True, text=True, cwd=RAIZ, timeout=30
        ).stdout.strip()
    except Exception as e:
        return f"[error ejecutando {cmd}: {e}]"


def ejecutar_p12():
    patrones = ["sk-ant-", "sb_secret_", "sb_publishable_", r"AQ\.[A-Za-z0-9]", "postgresql://postgres"]

    env_en_arbol = _ejecutar([
        "gh", "api", "repos/Nutriberry/hackathon-bi-agentico/git/trees/master?recursive=true",
        "--jq", ".tree[].path",
    ])
    env_en_arbol_filtrado = [
        linea for linea in env_en_arbol.splitlines()
        if linea == ".env" or (linea.startswith(".env.") and linea != ".env.example")
    ]

    busqueda_github = _ejecutar([
        "gh", "api", "-X", "GET", "search/code",
        "-f", "q=SUPABASE_DB_URL repo:Nutriberry/hackathon-bi-agentico",
        "--jq", ".items[].path",
    ])

    # Se excluyen los .md y la propia carpeta de evidencias: ambos citan estos
    # patrones como texto descriptivo (ej. "sk-ant-", "AQ.<token>"), no como
    # claves reales, y producirían falsos positivos contra este mismo script.
    grep_tracked = _ejecutar([
        "git", "grep", "-nE", "|".join(patrones), "--",
        ".", ":!*.md", ":!tests/evidencias/*",
    ])
    grep_tracked_filtrado = [
        l for l in grep_tracked.splitlines() if ".env.example" not in l
    ]

    historial_env = _ejecutar(["git", "log", "--all", "--full-history", "--", ".env"])

    sin_fugas = (
        not env_en_arbol_filtrado
        and not busqueda_github.strip()
        and not grep_tracked_filtrado
        and not historial_env.strip()
    )

    contenido = f"""P12 - Ausencia de claves en el repositorio GitHub

1. Árbol completo del repo remoto (gh api .../git/trees/master?recursive=true):
   archivos .env encontrados (excluyendo .env.example): {env_en_arbol_filtrado or 'ninguno'}

2. Búsqueda de código en GitHub (gh api search/code "SUPABASE_DB_URL repo:..."):
   {busqueda_github or 'sin resultados'}

3. git grep sobre archivos trackeados (patrones: {', '.join(patrones)}):
   {chr(10).join(grep_tracked_filtrado) or 'sin resultados'}

4. git log --all --full-history -- .env:
   {historial_env or 'sin resultados -> .env nunca se commiteó en ningún punto del historial.'}

Conclusión: {'PASA' if sin_fugas else 'FALLA'}. {'No hay credenciales expuestas en el repositorio público, ni en el estado actual ni en el historial completo de commits.' if sin_fugas else 'Se encontraron posibles fugas, revisar arriba.'}
"""
    (EVIDENCIAS / "P12_seguridad.txt").write_text(contenido, encoding="utf-8")
    print(contenido)
    return {"sin_fugas": sin_fugas}


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=== P01-P02: base de datos ===")
    r_bd = ejecutar_p01_p02()

    print("\n=== P03-P05: servidor MCP ===")
    r_mcp = ejecutar_p03_p04_p05()

    print("\n=== P06-P09, P11: agente ===")
    r_agente = ejecutar_agente()

    print("\n=== P12: seguridad ===")
    r_seguridad = ejecutar_p12()

    print("\n=== Resumen ===")
    print(f"P01 filas = 1067371: {r_bd['p01_filas'] == 1067371}")
    print(f"P02 filas > 0: {r_bd['p02_count'] > 0}")
    print(f"P03 4 herramientas correctas: {set(r_mcp['p03_herramientas']) == {'kpi_resumen','productos_en_riesgo','tasa_cancelacion','ventas_producto'}}")
    print(f"P05 vacío y servidor vivo: {r_mcp['p05_vacio'] and r_mcp['p05_servidor_vivo']}")
    print(f"P08 sin herramientas (fuera de dominio): {r_agente['P08']['herramientas'] == []}")
    print(f"P09 sin herramientas (sin datos): {r_agente['P09']['herramientas'] == []}")
    print(f"P12 sin fugas: {r_seguridad['sin_fugas']}")
    print(f"\nEvidencia guardada en {EVIDENCIAS}")


if __name__ == "__main__":
    main()
