# Registro de decisiones

Cada decisión en una línea, con su porqué. Sirve para la defensa y para REFLEXION.md.

| # | Fase | Decisión | Por qué |
|---|------|----------|---------|
| 1 | Preparación | Stack: Python + Supabase + FastMCP + Streamlit + GitHub | Lenguaje del curso, BD real en la nube, MCP oficial en Python y frontend sin escribir HTML |
| 2 | Preparación | Un solo agente coordinador | Cumple el requisito y reduce puntos de fallo en 5 h |
| 3 | Preparación | MCP propio con FastMCP (repo modelcontextprotocol/python-sdk) | Es MCP real y además cuenta como librería de GitHub adaptada |
| 4 | Preparación | Claves solo en .env; en el repo solo .env.example | Requisito de la entrega: no subir credenciales |
| 5 | Investigación | Sector retail / inventario | Experiencia previa del equipo y muchos datasets reales disponibles |
| 6 | Investigación | Problema 1: ABC y productos clave en riesgo (+ cancelaciones como KPI) | Datos reales, licencia clara, una tabla, comprobable con SQL y viable en el tiempo |
| 7 | Investigación | Corte ABC al 80 % de la facturación | Criterio clásico de Pareto, fácil de explicar y verificar |
| 8 | Investigación | Comparar con el mismo periodo del año anterior | Evita confundir la caída normal tras Navidad con un problema real |
| 9 | Desarrollo | Carga de datos con `COPY` (psycopg2 `copy_expert`) en vez de `to_sql` | `to_sql` inserta fila por fila y es demasiado lento para ~1M de filas |
| 10 | Desarrollo | `customer_id` como texto, no numérico, en la tabla `ventas` | El dataset trae muchos nulos y no se hace aritmética con ese campo; como texto se evita el problema de ".0" de los floats de pandas |
| 11 | Desarrollo | Conexión a Supabase vía "Session pooler" (puerto 5432), no la conexión directa | La conexión directa falla en redes con NAT/firewall restrictivo; el pooler es más compatible |
| 12 | Desarrollo | KPI calculados con SQL directo (CTEs), no en pandas | Los datos viven en Supabase; así el agente puede reusar las mismas consultas como fuente de verdad |
| 13 | Desarrollo | Filtrar siempre `NOT es_cancelacion AND price > 0` en los 3 KPI | Las cancelaciones y precios inválidos (regalos, ajustes contables) distorsionan la facturación real |
| 14 | Desarrollo | Modelo Gemini configurable en `.env` (`LLM_MODEL`); usamos `gemini-flash-lite-latest` porque `gemini-2.5-flash` está retirado | `gemini-2.5-flash` devuelve 404 (descontinuado); `LLM_MODEL` evita tocar código si vuelve a pasar. Aviso: "latest" significa que Google puede cambiar el modelo por detrás — si en la demo responde distinto a como lo probamos, esa es la causa |
| 15 | Desarrollo | Excluir `stock_code` que no empiezan por 5 cifras (`^[0-9]{5}`) en las 4 herramientas MCP y en los KPI de referencia | El dataset mezcla códigos que no son productos reales (POST, DOT, M, D "Discount", BANK CHARGES, AMAZONFEE, ADJUST, TEST..., gift_...) con artículos del catálogo; sin este filtro, "Discount" salía como el producto #1 en tasa de cancelación. Evidencia en `tests/evidencias/codigos_no_producto.txt` |
| 16 | Desarrollo | Cambiar `LLM_MODEL` de `gemini-flash-lite-latest` a `gemini-3.1-flash-lite` | El alias `latest` empezó a tardar 30s+ o dar 503 (capa gratuita saturada); probamos 5 modelos reales contra el endpoint de la API (no la doc, que no lista todos) y `gemini-3.1-flash-lite` fue el único consistentemente rápido (<1-3s en 4/4 pruebas) frente a `gemini-3.8-flash` (timeout), `gemini-3.7-flash` (503) y `gemini-3.5-flash-lite` (irregular, hasta 45s) |
