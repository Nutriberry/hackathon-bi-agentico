# Reparto del desarrollo (equipo de 4) y prompts

## Contrato común (NO cambiarlo sin avisar a todos)

**Servidor MCP** · `backend/mcp_server.py` · FastMCP, nombre `retail-bi`, transporte stdio.
Solo lectura sobre la tabla `ventas` de Supabase. Excluye cancelaciones y `price <= 0`
salvo en la tasa de cancelación. Si algo falla devuelve `{"error": "mensaje claro"}`.

| Herramienta | Parámetros | Devuelve |
|---|---|---|
| `kpi_resumen()` | — | `{facturacion_total, n_productos, n_productos_a, pct_facturacion_a}` |
| `productos_en_riesgo(umbral_caida=0.30, limite=10)` | float, int | lista de `{stock_code, description, ventas_2010, ventas_2011, variacion_pct}` (solo clase A, sep-nov 2011 vs sep-nov 2010) |
| `tasa_cancelacion(min_unidades=100, limite=10)` | int, int | lista de `{stock_code, description, unidades_vendidas, unidades_canceladas, tasa}` |
| `ventas_producto(stock_code)` | str | lista mensual de `{mes, unidades, importe}` |

**Agente** · `agents/agente.py` · función `responder(pregunta: str) -> dict` que devuelve
`{"respuesta": str, "herramientas_usadas": [{"nombre", "argumentos", "resultado"}]}`.

**Skill** · `skills/analisis-reposicion/SKILL.md` · el agente la lee y la añade a sus instrucciones.

**Frontend** · `frontend/app.py` · Streamlit, solo llama a `responder()`.

**Claves** · en `.env` (nunca en el repo). Giancarlo lo pasa por privado a quien lo necesite.

## Preparación para los integrantes nuevos (5 min)

```
git clone https://github.com/<usuario>/hackathon-bi-agentico.git
cd hackathon-bi-agentico
python -m venv .venv
# Mac/Linux: source .venv/bin/activate   ·   Windows: .venv\Scripts\activate
pip install -r requirements.txt
# crear .env copiando .env.example y pegar los valores que pase Giancarlo
```

Cada uno trabaja en su rama (`git checkout -b agente`, `frontend`...) y abre un Pull Request
al terminar. Así no se pisan los cambios.

---

## Prompt A · Giancarlo (Claude Code) · Servidor MCP

```
Sigue con el servidor MCP, pero SOLO el servidor: el agente y el frontend los hacen otros
compañeros en paralelo. Respeta exactamente el contrato de docs/prompts-equipo.md
(nombres de herramientas, parámetros y formato de salida).
1. Crea backend/db.py con una función consultar(sql, params) que lea SUPABASE_DB_URL de
   .env y devuelva una lista de diccionarios. Consultas siempre con parámetros, nunca
   concatenando texto.
2. Crea backend/mcp_server.py con FastMCP (paquete mcp, repo modelcontextprotocol/python-sdk),
   nombre "retail-bi", transporte stdio, con las 4 herramientas del contrato. Cada una con
   docstring clara en español, porque el LLM elige la herramienta leyendo esa descripción.
   Redondea decimales a 2. Captura errores y devuelve {"error": "..."}.
3. Crea tests/test_mcp.py que arranque el servidor como cliente MCP, liste las herramientas
   y llame a cada una, imprimiendo el resultado.
4. Comprueba que kpi_resumen y productos_en_riesgo dan los mismos valores que
   tests/kpi_referencia.md. Si no coinciden, dime por qué.
5. Explícame cómo conectar este servidor a Claude Desktop o Claude Code (archivo de
   configuración) para enseñarlo en la demo, sin poner claves en archivos del repo.
6. Commit y push a main. Resumen final en 5 líneas.
```

---

## Prompt B · Integrante 3 (su LLM) · Agente

```
Eres mi asistente de programación en un hackathon. Código simple, nivel curso, comentarios
breves en español. Tengo el repo hackathon-bi-agentico clonado, con .venv y .env.

OBJETIVO: crear agents/agente.py, un agente que responde preguntas de negocio sobre ventas
retail usando herramientas de un servidor MCP.

CONTRATO (no cambiarlo):
- El servidor MCP está en backend/mcp_server.py (FastMCP, stdio). Herramientas:
  kpi_resumen(), productos_en_riesgo(umbral_caida=0.30, limite=10),
  tasa_cancelacion(min_unidades=100, limite=10), ventas_producto(stock_code).
- Debo exponer: responder(pregunta: str) -> dict con
  {"respuesta": str, "herramientas_usadas": [{"nombre", "argumentos", "resultado"}]}

CÓMO:
1. Conecta como cliente MCP con el SDK oficial (from mcp import ClientSession,
   StdioServerParameters; from mcp.client.stdio import stdio_client), lanzando
   "python backend/mcp_server.py". Lista las herramientas del servidor.
2. LLM: Gemini API con el SDK google-genai y la clave LLM_API_KEY de .env (capa gratuita).
   Convierte cada herramienta MCP en una declaración de función para Gemini. Ojo: limpia
   del esquema JSON campos que Gemini no acepta (por ejemplo "title" o
   "additionalProperties") si da error.
3. Instrucciones del sistema = contenido de AGENTS.md + skills/analisis-reposicion/SKILL.md.
4. Bucle: el LLM pide herramienta → la ejecuto en el servidor MCP → le devuelvo el
   resultado → repito, máximo 5 vueltas. Luego respuesta final.
5. Reglas: responder en español, usar SOLO números que vengan de las herramientas, y si
   una herramienta devuelve error, decirlo en vez de inventar.
6. Guarda cada pregunta, herramientas usadas y respuesta en logs/agente.log (evidencia
   para las pruebas). Añade logs/ al .gitignore.
7. Como responder() lo usará Streamlit, que no es asíncrono, envuelve la parte async con
   asyncio.run dentro de responder().
8. Añade al final un bloque if __name__ == "__main__" que pregunte
   "¿Qué productos importantes están cayendo?" e imprima el resultado.
9. Añade google-genai a requirements.txt.
Si el servidor MCP aún no existe, crea primero un servidor falso mínimo en
tests/mcp_falso.py con las mismas 4 herramientas devolviendo datos de ejemplo, para
poder avanzar, y deja una variable para cambiar entre falso y real.
Trabaja en la rama "agente" y al final explícame cómo abrir el Pull Request.
```

---

## Prompt C · Integrante 4 (su LLM) · Frontend Streamlit

```
Eres mi asistente de programación en un hackathon. Código simple, nivel curso, comentarios
breves en español. Tengo el repo hackathon-bi-agentico clonado, con .venv y .env.

OBJETIVO: crear frontend/app.py en Streamlit para un agente de BI de retail.

CONTRATO (no cambiarlo): importo responder desde agents/agente.py.
responder(pregunta: str) -> {"respuesta": str,
  "herramientas_usadas": [{"nombre", "argumentos", "resultado"}]}

PANTALLA:
1. Título "Agente de BI · Productos clave en riesgo" y una línea explicando el problema.
2. Barra lateral con 4 botones de preguntas de ejemplo:
   - "Dame el resumen de KPI"
   - "¿Qué productos importantes están cayendo?"
   - "¿Qué productos tienen más cancelaciones?"
   - "¿Qué recomiendas reponer o revisar?"
3. Chat (st.chat_input y st.chat_message) que guarda el historial en st.session_state.
4. Debajo de cada respuesta, un desplegable "Cómo lo ha calculado" con cada herramienta
   usada, sus argumentos y su resultado; si el resultado es una lista, mostrarlo como
   tabla (pandas DataFrame) y, si tiene una columna numérica, un gráfico de barras simple.
5. Spinner mientras responde y mensaje de error claro si algo falla.
6. Hasta que el agente esté listo, usa una función responder_falso() con datos de ejemplo
   y un interruptor en la barra lateral "Modo demo / Modo real".
Para que el import funcione desde frontend/, añade la carpeta raíz al sys.path.
Se arranca con: streamlit run frontend/app.py (ponlo en un comentario arriba).
Trabaja en la rama "frontend" y al final explícame cómo abrir el Pull Request.
```

---

## Prompt D · Compañera (Gemini) · Arquitectura, agente y Skill

Pegar primero el contrato común de arriba y luego:

```
Con este contrato, redacta en Markdown estos 3 archivos para un sistema agéntico de BI
(problema: clasificación ABC y productos clave en riesgo en una tienda online, datos reales
Online Retail II en Supabase). Lenguaje claro, sin jerga.

1. docs/arquitectura.md
   - Diagrama Mermaid (flowchart TD): Usuario → Streamlit → Agente (Gemini) →
     Skill analisis-reposicion y Servidor MCP retail-bi → Supabase (tabla ventas) →
     Resultado BI.
   - Tabla de componentes: qué hace, tecnología, archivo.
   - Flujo de una pregunta paso a paso.
   - Errores previstos y cómo se manejan (BD caída, herramienta con error, pregunta fuera
     de tema, LLM inventa números).
   - Acciones que requieren autorización humana: el agente solo recomienda; nunca crea
     pedidos ni modifica datos.
   - Librería de GitHub adaptada: modelcontextprotocol/python-sdk (FastMCP).

2. AGENTS.md
   - Rol del agente, a quién ayuda, qué puede y qué no puede hacer.
   - Sus 4 herramientas y cuándo usar cada una.
   - Reglas: responder en español, solo números que vengan de herramientas, citar la
     herramienta usada, decir "no tengo datos para eso" si no puede responder.

3. skills/analisis-reposicion/SKILL.md
   Empieza con este encabezado:
   ---
   name: analisis-reposicion
   description: Analiza qué productos clave están en riesgo y recomienda qué reponer o revisar.
   ---
   Después, el proceso en pasos numerados:
   1) kpi_resumen para el contexto; 2) productos_en_riesgo; 3) tasa_cancelacion y cruzar
   con los productos en riesgo; 4) recomendar con estas reglas: en riesgo y con alta
   cancelación → revisar calidad o proveedor; en riesgo sin cancelaciones altas → reducir
   reposición o lanzar promoción; 5) formato de salida: resumen de 3 líneas, tabla de
   productos y recomendación por producto, citando los números.
```
