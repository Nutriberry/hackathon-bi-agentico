# Plan de Pruebas y Validación del Sistema Agéntico de BI

Las pruebas P01–P09 y P12 se ejecutan de forma automática con `tests/ejecutar_pruebas.py` (consultas SQL a Supabase, llamadas al servidor MCP y preguntas al agente) y guardan su salida en `tests/evidencias/`. Las pruebas P10 y P11 se hacen a mano en la aplicación Streamlit, con capturas de pantalla como evidencia.

---

## Tabla Resumen de Pruebas

| ID | Componente | Qué se prueba | Entrada | Resultado esperado | Resultado obtenido | Estado | Evidencia |
|---|---|---|---|---|---|---|---|
| **P01** | Base de datos | Conteo total de registros en Supabase | `SELECT count(*) FROM ventas;` | Mismo número de filas que en el Excel original (`Online Retail II`). | | Pendiente | |
| **P02** | Base de datos | Consulta de un producto concreto | `SELECT * FROM ventas WHERE stock_code = '85123A';` | Devuelve las filas correspondientes al código de stock. | | Pendiente | |
| **P03** | Servidor MCP | Listado de herramientas disponibles en `retail-bi` | Petición para listar herramientas MCP | Aparecen exactamente las 4 herramientas: `kpi_resumen`, `productos_en_riesgo`, `tasa_cancelacion` y `ventas_producto`. | | Pendiente | |
| **P04** | Servidor MCP | Validación de los cálculos de KPIs | Llamada directa a `kpi_resumen` | Los valores obtenidos coinciden con los documentados en `tests/kpi_referencia.md`. | | Pendiente | |
| **P05** | Servidor MCP | Manejo de errores y valores inexistentes | Llamada a `ventas_producto` con `stock_code = "XXXX"` | Devuelve una lista vacía o un error claro de forma controlada, sin caer el servidor. | | Pendiente | |
| **P06** | Skill | Recomendaciones de reposición integradas | Pregunta: *"¿Qué recomiendas reponer o revisar?"* | El agente invoca `kpi_resumen`, `productos_en_riesgo` y `tasa_cancelacion`, ofreciendo una recomendación por producto. | | Pendiente | |
| **P07** | Agente Gemini | Detección de productos con caída en ventas | Pregunta: *"¿Qué productos importantes están cayendo?"* | Utiliza la herramienta `productos_en_riesgo` y los números devueltos coinciden con `tests/kpi_referencia.md`. | | Pendiente | |
| **P08** | Agente Gemini | Delimitación del dominio y fuera de ámbito | Pregunta: *"¿Qué tiempo hace en Madrid?"* | El agente se niega amablemente a responder sin invocar ninguna herramienta. | | Pendiente | |
| **P09** | Agente Gemini | Control de alucinaciones ante datos no disponibles | Pregunta: *"¿Cuál es el stock actual?"* | Responde claramente que no dispone de dichos datos, absteniéndose de inventar cifras. | | Pendiente | |
| **P10** | Frontend Streamlit | Interfaz interactiva y explicabilidad (4 botones) | Abrir app en Modo Real y pulsar los 4 botones predefinidos | Muestra la respuesta del agente y el desplegable *"Cómo lo ha calculado"* conteniendo la tabla correspondiente. | Los 4 botones responden con datos reales y citan la herramienta usada (`kpi_resumen`, `productos_en_riesgo`, `tasa_cancelacion`). Se detectó además un error 503 de Gemini sin tratar, ya corregido con reintentos. | Pasada | `tests/evidencias/P10_1_resumen_kpi.png`, `P10_2_productos_cayendo.png`, `P10_3_cancelaciones.png`, `P10_4_recomendacion.png`, `P10_error_503.png` |
| **P11** | Flujo Completo | Integración End-to-End desde la UI | Pregunta escrita manualmente en el chat interactivo | Muestra la respuesta contextualizada utilizando los datos reales almacenados en Supabase. | | Pendiente | |
| **P12** | Seguridad | Exposición de credenciales e ignorado de entorno | Búsqueda global de `.env`, claves API o secretos en el repositorio GitHub | La búsqueda no arroja ningún resultado ni archivo de entorno subido. | | Pendiente | |

---

## Detalle de Pruebas

### P01 - Base de datos: Conteo total de registros
* **Qué se prueba:** Verificación de la integridad de la carga inicial de datos en Supabase.
* **Entrada:** `SELECT count(*) FROM ventas;`
* **Esperado:** Mismo número de filas que el archivo Excel de origen (`Online Retail II`).
* **Obtenido:** 
* **Estado:** Pendiente
* **Evidencia:** 
* **Si falla (causa y corrección):** 

---

### P02 - Base de datos: Consulta de un producto concreto
* **Qué se prueba:** Correcta indexación y recuperación de datos por código de producto.
* **Entrada:** `SELECT * FROM ventas WHERE stock_code = '85123A';`
* **Esperado:** Devuelve los registros asociados al producto especificado.
* **Obtenido:** 
* **Estado:** Pendiente
* **Evidencia:** 
* **Si falla (causa y corrección):** 

---

### P03 - MCP: Listar herramientas del servidor
* **Qué se prueba:** Disponibilidad y registro de todas las herramientas expuestas por FastMCP.
* **Entrada:** Petición de listado de herramientas al servidor `retail-bi`.
* **Esperado:** Se listan 4 herramientas: `kpi_resumen`, `productos_en_riesgo`, `tasa_cancelacion` y `ventas_producto`.
* **Obtenido:** 
* **Estado:** Pendiente
* **Evidencia:** 
* **Si falla (causa y corrección):** 

---

### P04 - MCP: Llamar a kpi_resumen
* **Qué se prueba:** Precisión de los datos devueltos por la herramienta de KPIs básicos.
* **Entrada:** Ejecución de la herramienta `kpi_resumen`.
* **Esperado:** Mismos valores que los especificados en el archivo de referencia `tests/kpi_referencia.md`.
* **Obtenido:** 
* **Estado:** Pendiente
* **Evidencia:** 
* **Si falla (causa y corrección):** 

---

### P05 - MCP: Llamar a ventas_producto con un código inexistente
* **Qué se prueba:** Resiliencia y manejo de excepciones en herramientas MCP ante entradas no encontradas.
* **Entrada:** Llamada a `ventas_producto` pasándole el código `"XXXX"`.
* **Esperado:** Devuelve una lista vacía o un mensaje de error claro sin interrumpir el servicio ni tirar el servidor FastMCP.
* **Obtenido:** 
* **Estado:** Pendiente
* **Evidencia:** 
* **Si falla (causa y corrección):** 

---

### P06 - Skill: Preguntar por recomendaciones de reposición
* **Qué se prueba:** Capacidad del agente para orquestar múltiples herramientas y aplicar la lógica del Skill `analisis-reposicion`.
* **Entrada:** *"¿Qué recomiendas reponer o revisar?"*
* **Esperado:** El agente invoca secuencialmente `kpi_resumen`, `productos_en_riesgo` y `tasa_cancelacion`, devolviendo una recomendación detallada por producto.
* **Obtenido:** 
* **Estado:** Pendiente
* **Evidencia:** 
* **Si falla (causa y corrección):** 

---

### P07 - Agente: Identificación de productos en caída
* **Qué se prueba:** Utilización adecuada de herramientas específicas e interpretación de métricas.
* **Entrada:** *"¿Qué productos importantes están cayendo?"*
* **Esperado:** Llama a la herramienta `productos_en_riesgo` y las cifras en la respuesta coinciden con `tests/kpi_referencia.md`.
* **Obtenido:** 
* **Estado:** Pendiente
* **Evidencia:** 
* **Si falla (causa y corrección):** 

---

### P08 - Agente: Fuera de dominio
* **Qué se prueba:** Límites de consulta e instrucción de no responder temas ajenos al negocio de BI.
* **Entrada:** *"¿Qué tiempo hace en Madrid?"*
* **Esperado:** El agente rechaza responder de forma cortés y no ejecuta ninguna herramienta MCP.
* **Obtenido:** 
* **Estado:** Pendiente
* **Evidencia:** 
* **Si falla (causa y corrección):** 

---

### P09 - Agente: Datos no disponibles en el sistema
* **Qué se prueba:** Ausencia de alucinaciones sobre variables no presentes en la base de datos (p. ej. stock físico).
* **Entrada:** *"¿Cuál es el stock actual?"*
* **Esperado:** El agente declara que no dispone de esa información sin inventar o asumir valores.
* **Obtenido:** 
* **Estado:** Pendiente
* **Evidencia:** 
* **Si falla (causa y corrección):** 

---

### P10 - Frontend: Interfaz Streamlit y botones de acceso rápido
* **Qué se prueba:** Integración con la UI, ejecución de los 4 botones predefinidos y visibilidad del razonamiento/cálculos.
* **Entrada:** Selección del Modo Real en Streamlit y pulsación de cada uno de los 4 botones.
* **Esperado:** Muestra la respuesta generada y despliega la sección *"Cómo lo ha calculado"* incorporando la tabla con el desglose.
* **Obtenido:**
  * *"Dame el resumen de KPI"* → facturación total 20.108.995,40, 4.878 productos, 1.036 clase A, 80,02 % — cita la herramienta `kpi_resumen`.
  * *"¿Qué productos importantes están cayendo?"* → lista de productos clase A con variación -100 % (RED WHITE SCARF HOT WATER BOTTLE, WHITE DOVE HONEYCOMB PAPER GARLAND, SET OF THREE VINTAGE GIFT WRAPS...) vía `productos_en_riesgo`.
  * *"¿Qué productos tienen más cancelaciones?"* → tabla con BLACK CHERRY LIGHTS (102,06 %), PAPER CRAFT LITTLE BIRDIE (100 %), LITTLE FLOWER SHOPPER BAG (100 %), MEDIUM CERAMIC TOP STORAGE JAR (95,46 %) vía `tasa_cancelacion`; ya no aparece "Discount" (ver decisión #15 en `docs/decisiones.md`).
  * *"¿Qué recomiendas reponer o revisar?"* → resumen inicial + tabla por producto con acción recomendada (ej. SET OF 3 CASES WOODLAND DESIGN → "Reducir reposición o lanzar promoción").
* **Estado:** Pasada
* **Evidencia:** `tests/evidencias/P10_1_resumen_kpi.png`, `P10_2_productos_cayendo.png`, `P10_3_cancelaciones.png`, `P10_4_recomendacion.png`
* **Si falla (causa y corrección):** Durante la prueba apareció una vez el error crudo *"Algo ha fallado al responder: unhandled errors in a TaskGroup (1 sub-exception)"* al pulsar *"¿Qué productos tienen más cancelaciones?"* (captura `P10_error_503.png`) — causa: error 503 de Gemini (servicio saturado) sin capturar en `agents/agente.py`. Corregido con reintentos automáticos (5 s/10 s/20 s) y mensaje claro en vez de la excepción cruda (commit "Reintentos y mensaje claro ante 503/429 de Gemini").

---

### P11 - Flujo completo: Consulta libre en el chat
* **Qué se prueba:** Integración End-to-End desde el prompt de usuario en el frontend hasta la consulta a Supabase y respuesta del LLM.
* **Entrada:** Pregunta personalizada introducida manualmente en la caja de chat.
* **Esperado:** Respuesta precisa construida a partir de los datos reales alojados en la base de datos.
* **Obtenido:** 
* **Estado:** Pendiente
* **Evidencia:** 
* **Si falla (causa y corrección):** 

---

### P12 - Seguridad: Ausencia de claves en el repositorio
* **Qué se prueba:** Prevención de fugas de secretos y verificación de archivos sensiblemente excluidos (`.gitignore`).
* **Entrada:** Búsqueda textual y de patrones de claves/archivos `.env` en el repositorio público/privado de GitHub.
* **Esperado:** Búsqueda sin resultados de credenciales expuestas.
* **Obtenido:** 
* **Estado:** Pendiente
* **Evidencia:** 
* **Si falla (causa y corrección):** 

---

## Errores encontrados y limitaciones

1. **`productos_en_riesgo` devuelve sobre todo productos con caída del -100 %** (ventas 2011 = 0 en el periodo sep-nov), que probablemente están descatalogados en vez de "en riesgo" (caída parcial de demanda). *Mejora propuesta:* separar "descatalogados" (ventas 2011 = 0) de "en caída" (variación entre -30 % y -99 %), para no mezclar ambos casos en el mismo listado.
2. **`tasa_cancelacion` está dominada por pedidos únicos anulados enteros** (ej. `23843` PAPER CRAFT, LITTLE BIRDIE: 80.995 unidades vendidas = 80.995 canceladas) y por tasas superiores al 100 % (cancelaciones de compras anteriores a diciembre de 2009, fuera del rango del dataset, por lo que las "vendidas" correspondientes no se contabilizan). *Mejora propuesta:* contar pedidos (`invoice`) cancelados en vez de unidades, o exigir un mínimo de pedidos distintos además del mínimo de unidades.
3. **Error 503 de Gemini ("servicio no disponible") intermitente** al llamar a la API durante picos de uso de la capa gratuita. *Corrección aplicada:* reintentos automáticos en `agents/agente.py` con espera creciente (5 s, 10 s, 20 s) ante 503/429, y mensaje claro al usuario ("el servicio de Gemini está saturado, inténtalo en unos segundos" / "se ha superado la cuota gratuita, espera un minuto") si los reintentos se agotan, en vez de un error técnico o una caída silenciosa.
