# Tareas del equipo · Pruebas, README, presentación y reflexión (19:00 – 21:00)

Giancarlo está integrando y probando el sistema en su ordenador. Vosotros preparáis los
documentos en paralelo con vuestro LLM. **Entregad todo a Giancarlo en archivos .md**
(texto plano o bloque de código, no Google Docs, porque mete símbolos raros).

---

## Compañera · Batería de pruebas → `tests/pruebas.md` (30 min)

**Paso 1.** En Gemini, chat nuevo, pega:

```
Redacta en Markdown el archivo tests/pruebas.md de un sistema agéntico de BI
(frontend Streamlit → agente Gemini → Skill analisis-reposicion y servidor MCP
"retail-bi" con FastMCP → base de datos Supabase, tabla ventas del dataset real
Online Retail II).

Estructura:
1. Una línea explicando cómo se han hecho las pruebas.
2. Tabla resumen con columnas: ID | Componente | Qué se prueba | Entrada |
   Resultado esperado | Resultado obtenido | Estado | Evidencia
   Deja "Resultado obtenido" y "Evidencia" vacíos y "Estado" como "Pendiente".
3. Una sección por prueba con: Qué se prueba, Entrada, Esperado, Obtenido (vacío),
   Estado, Evidencia (vacío), Si falla: causa y corrección (vacío).
4. Sección final "Errores encontrados y limitaciones" vacía.

Estas son las pruebas (no inventes otras):
P01 Base de datos: SELECT count(*) FROM ventas → mismo número de filas que el Excel.
P02 Base de datos: consulta de un producto concreto (stock_code 85123A) → devuelve filas.
P03 MCP: listar herramientas del servidor → aparecen 4: kpi_resumen, productos_en_riesgo,
    tasa_cancelacion, ventas_producto.
P04 MCP: llamar a kpi_resumen → mismos valores que tests/kpi_referencia.md.
P05 MCP: llamar a ventas_producto con un código inexistente "XXXX" → lista vacía o
    error claro, sin que el servidor se caiga.
P06 Skill: preguntar "¿Qué recomiendas reponer o revisar?" → el agente usa
    kpi_resumen, productos_en_riesgo y tasa_cancelacion y da una recomendación por producto.
P07 Agente: "¿Qué productos importantes están cayendo?" → usa productos_en_riesgo y los
    números coinciden con kpi_referencia.md.
P08 Agente: "¿Qué tiempo hace en Madrid?" → se niega amablemente sin usar herramientas.
P09 Agente: pregunta por un dato que no existe ("¿cuál es el stock actual?") → dice que
    no tiene datos, sin inventar cifras.
P10 Frontend: abrir la app en Modo real y pulsar los 4 botones → respuesta y desplegable
    "Cómo lo ha calculado" con tabla.
P11 Flujo completo: pregunta escrita en el chat → respuesta con datos reales de Supabase.
P12 Seguridad: el repo de GitHub no contiene .env ni claves → búsqueda sin resultados.
```

**Paso 2.** Revisa que salen las 12 pruebas y la tabla está bien formada.
**Paso 3.** Envía el archivo `pruebas.md` a Giancarlo.
**Paso 4.** Cuando Giancarlo te pase las capturas y resultados, pide a Gemini rellenar
"Obtenido", "Estado" y "Evidencia" **solo con lo que él te pase**.

---

## Integrante 3 · README del proyecto → `README.md` (25 min)

**Paso 1.** En tu LLM, pega:

```
Redacta el README.md de un repositorio de GitHub para un proyecto académico
(hackathon INESDI, Business Intelligence × IA agéntica). Lenguaje claro.

Proyecto: agente de BI que detecta productos clave en riesgo en una tienda online.
Clasificación ABC (clase A = 80 % de la facturación), productos A cuyas ventas
sep-nov 2011 caen >30 % frente a sep-nov 2010, y tasa de cancelación por producto.
Datos reales: Online Retail II (UCI, licencia CC BY 4.0) cargados en Supabase (Postgres).

Arquitectura: frontend Streamlit → agente Python con Gemini API (tool calling) →
Skill propia analisis-reposicion + servidor MCP propio "retail-bi" hecho con FastMCP
(librería de GitHub modelcontextprotocol/python-sdk) → Supabase.

Secciones:
1. Título y descripción en 3 líneas
2. Problema y usuario (enlace a investigacion/problema.md)
3. Arquitectura (enlace a docs/arquitectura.md) y tabla de componentes
4. Estructura de carpetas: README.md, AGENTS.md, CLAUDE.md, .env.example, investigacion/,
   docs/, agents/agente.py, skills/analisis-reposicion/SKILL.md, data/ (fuente.md,
   perfil_datos.md, muestra_1000.csv), backend/ (cargar_datos.py, perfilar_datos.py,
   kpi_referencia.py, db.py, mcp_server.py), frontend/app.py, tests/ (pruebas.md,
   kpi_referencia.md, test_mcp.py, mcp_falso.py), REFLEXION.md
5. Requisitos: Python 3.12, cuenta Supabase gratuita, clave de Gemini API gratuita
6. Instalación paso a paso en Windows: clonar, python -m venv .venv,
   .venv\Scripts\activate, pip install -r requirements.txt, copiar .env.example a .env
   y rellenar SUPABASE_DB_URL y LLM_API_KEY
7. Carga de datos: descargar el Excel de UCI en data/raw/ y ejecutar
   python backend/cargar_datos.py
8. Ejecución: python tests/test_mcp.py (probar MCP), python agents/agente.py
   (probar agente), streamlit run frontend/app.py (aplicación)
9. Preguntas de ejemplo (las 4 de la app)
10. Pruebas (enlace a tests/pruebas.md)
11. Limitaciones: sin datos de stock, datos 2009-2011, depende de la cuota gratuita de Gemini
12. Equipo: 4 integrantes (deja los nombres como [Nombre 1]...[Nombre 4]) y aviso de que
    no se suben claves (.env está en .gitignore)
```

**Paso 2.** Sustituye [Nombre 1..4] por los nombres reales.
**Paso 3.** Envía `README.md` a Giancarlo.

---

## Integrante 4 · Guion de la presentación → `docs/presentacion.md` (25 min)

**Paso 1.** En tu LLM, pega:

```
Prepara el guion de una presentación de 10 minutos con demo en directo, en Markdown,
para defender un sistema agéntico de BI en un hackathon (4 integrantes). Proyecto:
agente que detecta productos clave (clase A) con ventas en caída y cancelaciones altas
en una tienda online, con datos reales Online Retail II en Supabase, servidor MCP
propio (FastMCP), Skill propia "analisis-reposicion", agente con Gemini y Streamlit.

Bloques obligatorios (con minutos y quién habla, como Persona 1..4):
1. Problema, investigación y oportunidad (2 min)
2. Arquitectura, Skill, MCP y base de datos (2 min)
3. Demo en directo de principio a fin: pregunta en la app → herramientas usadas →
   respuesta con datos reales (3 min). Incluye las 3 preguntas a hacer en la demo y
   un plan B si falla internet (capturas preparadas).
4. Batería de pruebas: cuántas pasaron, errores encontrados y cómo se corrigieron (2 min)
5. Reflexión y aprendizajes (1 min)
Añade al final 10 preguntas difíciles que podría hacer el profesor, con respuesta corta.
Ejemplos: ¿por qué 80 %?, ¿por qué comparar con el año anterior?, ¿cómo sabéis que el
agente no inventa números?, ¿qué pasa sin stock real?, ¿por qué un solo agente?,
¿qué librería de GitHub adaptasteis?, ¿qué haría falta para usarlo en producción?
```

**Paso 2.** Repartid los bloques entre los 4 y sustituid "Persona 1..4" por nombres.
**Paso 3.** Envía `presentacion.md` a Giancarlo.

---

## TODOS · Reflexión individual → `REFLEXION.md` (15 min, a partir de las 20:30)

Cada uno escribe **con sus palabras** (no con IA: se valora la honestidad) y envía a
Giancarlo un texto con su nombre y estas 5 respuestas:

1. ¿Qué he aprendido hoy?
2. ¿Qué me llevo y cómo lo aplicaré?
3. ¿Dónde me he bloqueado y cómo lo he afrontado?
4. ¿Qué he aportado al equipo?
5. ¿Qué haría diferente la próxima vez?

Ideas reales de hoy que podéis usar si os encajan: llegar con el reto empezado y tener
que entender un contrato ya definido; Gemini se inventó una herramienta que no existía
(`clasificacion_abc`) y entregó tres archivos iguales; trabajar con un archivo de
contrato para no pisarse; probar con datos falsos antes del real.

Después, **los 4 juntos (10 min)** responden la reflexión colectiva:
1. ¿Qué hemos aprendido trabajando juntos?
2. ¿Qué nos llevamos de esta experiencia?
3. ¿Dónde nos hemos bloqueado y cómo lo hemos resuelto?
4. ¿Cómo hemos decidido, escuchado y cuestionado a la IA?
5. ¿Qué haríamos diferente si empezáramos de nuevo?
Y los 3 compromisos: **Vamos a mantener… · Vamos a cambiar… · Vamos a experimentar…**
