# Guion de la presentación (10 min + preguntas)

**Proyecto:** agente de BI que detecta productos clave (clase A) con ventas en caída y
cancelaciones altas en una tienda online.

| Bloque | Tiempo | Minuto | Habla |
|---|---|---|---|
| 1. Problema, investigación y oportunidad | 2 min | 0:00 – 2:00 | Angello Pequeño |
| 2. Arquitectura, Skill, MCP y base de datos | 2 min | 2:00 – 4:00 | María José Girón |
| 3. Demo en directo | 3 min | 4:00 – 7:00 | Rafael Celis |
| 4. Batería de pruebas | 2 min | 7:00 – 9:00 | Giancarlo De las Casas |
| 5. Reflexión y aprendizajes | 1 min | 9:00 – 10:00 | Todos (15 s cada uno) |

> Reparto propuesto: cada uno presenta lo que ha hecho. Cambiad el reparto
> si os organizáis de otra forma.

---

## Bloque 1 · Problema, investigación y oportunidad (2 min) · Angello Pequeño

**Qué decir:**

- **Usuario:** el responsable de compras de una pyme de comercio online con cientos de
  productos.
- **Problema:** no sabe de un vistazo qué productos sostienen el negocio ni cuáles de esos
  se están frenando. Lo descubre tarde, revisando hojas de cálculo a mano.
- **Cómo lo resuelven hoy las empresas:** Excel manual, módulos ABC de ERP (SAP, NetSuite)
  con reglas fijas, o herramientas SaaS de planificación (Slimstock, Inventory Planner,
  ToolsGroup, Cin7). Problemas: reglas estáticas, dashboards pasivos y demasiadas alertas
  sin prioridad.
- **Cómo elegimos el problema:** comparamos 5 problemas con 4 datasets distintos y nos
  quedamos con el de clasificación ABC y productos en riesgo. Datos reales con licencia
  clara, una sola tabla, resultado comprobable con SQL y viable en el tiempo del hackathon.
- **Oportunidad:** en vez de un dashboard al que hay que ir a buscar, un agente al que se
  le pregunta en lenguaje normal y responde con la lista, los números y una recomendación.
- **Los 3 KPI:**
  1. % de facturación que concentra la clase A.
  2. Productos A cuyas ventas de sep-nov 2011 caen más de un 30 % frente a sep-nov 2010.
  3. Tasa de cancelación por producto.

**Frase de cierre:** "Uno de cada cinco productos genera el 80 % del dinero. Si uno de esos
se cae, hay que saberlo ya, no a final de trimestre."

---

## Bloque 2 · Arquitectura, Skill, MCP y base de datos (2 min) · María José Girón

**Mostrar:** el diagrama de `docs/arquitectura.md`.

```
Usuario → Streamlit → Agente (Gemini) → Skill analisis-reposicion
                                      → Servidor MCP retail-bi → Supabase (tabla ventas)
```

**Qué decir:**

- **Datos:** Online Retail II (UCI, licencia CC BY 4.0). Son **1.067.371 transacciones
  reales** de una tienda online británica, entre dic-2009 y dic-2011, de 43 países.
  Están cargadas en **Supabase** (Postgres en la nube).
- **Servidor MCP propio "retail-bi"**, hecho con **FastMCP**, la librería de GitHub
  `modelcontextprotocol/python-sdk`. Tiene 4 herramientas de solo lectura:
  `kpi_resumen`, `productos_en_riesgo`, `tasa_cancelacion` y `ventas_producto`.
  El agente no escribe SQL: solo puede usar estas 4 herramientas, con consultas
  parametrizadas.
- **Skill propia "analisis-reposicion":** es el procedimiento que sigue el agente cuando
  le preguntan qué reponer o revisar:
  1. Pide los KPI.
  2. Busca los productos en riesgo.
  3. Cruza esa lista con las cancelaciones.
  4. Recomienda según dos reglas:
     - En riesgo y con alta cancelación → **revisar calidad o proveedor**.
     - En riesgo sin cancelaciones altas → **reducir reposición o lanzar promoción**.
- **Agente:** Gemini 2.5 Flash con *tool calling*. Hace como máximo 5 vueltas de
  herramienta y respuesta, y guarda cada consulta en `logs/agente.log`.
- **Límite deliberado:** el agente solo recomienda. Nunca crea pedidos ni modifica datos.
  La decisión es siempre humana.

---

## Bloque 3 · Demo en directo (3 min) · Rafael Celis

**Antes de empezar (preparado ANTES de subir):**
- App abierta con `streamlit run frontend/app.py`, en **Modo real** y con el historial
  limpio.
- Pestaña con las capturas del plan B abierta, pero oculta.
- Haber hecho una pregunta de calentamiento 5 minutos antes, para comprobar que Supabase
  y Gemini responden.

**Las 3 preguntas de la demo:**

| # | Pregunta | Qué enseñar | Dato que debe salir |
|---|---|---|---|
| 1 | "Dame el resumen de KPI" (botón) | La respuesta y el desplegable "Cómo lo ha calculado" con `kpi_resumen` | Facturación 20.108.995,40 · 1.036 productos A de 4.878 · **80,02 %** de la facturación |
| 2 | "¿Qué productos importantes están cayendo?" (botón) | La tabla y el gráfico de barras de `productos_en_riesgo` | Productos A que caen más de un 30 %: 472 en total, 66 de ellos sin ninguna venta en sep-nov 2011 |
| 3 | "¿Qué recomiendas reponer o revisar?" (escrita en el chat) | Que usa **varias herramientas** siguiendo la Skill y da una recomendación por producto | Acción por producto citando sus números |

**Qué decir mientras carga:** "Lo importante no es solo la respuesta: en el desplegable
se ve qué herramienta ha usado, con qué parámetros y qué ha devuelto la base de datos.
Cualquier número de la respuesta se puede comprobar aquí."

**Plan B si falla internet, Supabase o Gemini:**
1. **Primero:** cambiar el interruptor de la barra lateral a **"Modo demo"**. La app
   funciona sin internet, con los mismos datos reales guardados de antemano. Hay que
   decirlo en voz alta: "Estamos en modo demo por la conexión; son los mismos datos
   reales, guardados".
2. **Si tampoco arranca la app:** enseñar las capturas en Modo real de `tests/evidencias/`
   (`P10_1_resumen_kpi.png` … `P10_4_recomendacion.png`), una por cada botón, y la
   salida del agente en `P06_P07_P08_P09_P11_agente.txt`.

> Ojo: no usar las capturas de `docs/capturas/` (modo demo), porque muestran las cifras
> de antes de quitar los códigos que no son productos (20.972.594,57 y 1.005 productos A).

---

## Bloque 4 · Batería de pruebas (2 min) · Giancarlo De las Casas

**Mostrar:** la tabla resumen de `tests/pruebas.md`.

**Qué decir:**

- Hicimos **12 pruebas** por capas: base de datos (P01–P02), servidor MCP (P03–P05),
  Skill (P06), agente (P07–P09), frontend (P10), flujo completo (P11) y seguridad (P12).
- **Resultado: 12 de 12 superadas.** P01–P09, P11 y P12 se automatizaron con
  `tests/ejecutar_pruebas.py`; P10 y P11 se comprobaron también a mano en la app, con
  capturas. Todas las evidencias están en `tests/evidencias/`.
- **Cómo sabemos que los números son correctos:** calculamos los KPI por otro camino, con
  SQL directo (`tests/kpi_referencia.md`), y comprobamos que el agente da los mismos
  valores (P04 y P07).
- **Errores encontrados y cómo se corrigieron:**

| Error | Causa | Corrección |
|---|---|---|
| La carga de ~1 M de filas era lentísima | `to_sql` inserta fila por fila | Carga con `COPY` (psycopg2 `copy_expert`) |
| No conectaba con Supabase desde algunas redes | La conexión directa falla con NAT/firewall | Usar el *Session pooler* (puerto 5432) |
| El agente dejó de funcionar | Cambió la API del paquete `mcp` (versión 2.x) y Google retiró el modelo de Gemini que usábamos | Código adaptado a la nueva API y modelo configurable desde `.env` (`LLM_MODEL`) |
| "Discount" (código D) salía como el producto n.º 1 en cancelaciones, con una tasa de 1.565 % | El dataset mezcla 62 códigos que no son productos (portes, comisiones, descuentos, ajustes, pruebas…): 6.093 filas | Solo se cuentan los `stock_code` que empiezan por 5 cifras, en las 4 herramientas y en los KPI de referencia (evidencia en `tests/evidencias/codigos_no_producto.txt`) |
| Gemini fallaba a ratos con error 503/429 | La capa gratuita se satura o se agota la cuota | Reintentos automáticos (5 s, 10 s, 20 s) y mensaje claro al usuario si se agotan |

**Limitaciones conocidas (decirlas antes de que las pregunten):** `productos_en_riesgo`
mezcla productos descatalogados (ventas a 0) con productos en caída parcial, y
`tasa_cancelacion` la dominan pedidos únicos anulados enteros. Mejoras propuestas:
separar ambos casos y contar pedidos cancelados en vez de unidades.

---

## Bloque 5 · Reflexión y aprendizajes (1 min) · Todos

Unos 15 segundos cada uno, una idea por persona:

- **Angello Pequeño:** elegir el problema con criterios (datos reales, una tabla,
  comprobable) nos ahorró horas. El problema más vistoso no era el más viable.
- **María José Girón:** separar herramientas (MCP), procedimiento (Skill) y reglas
  (AGENTS.md) hace que cada pieza se pueda cambiar sin romper las demás.
- **Rafael Celis:** acordar el contrato entre piezas desde el principio permitió trabajar los 4
  en paralelo. El frontend se hizo con un agente falso y encajó a la primera.
- **Giancarlo De las Casas:** un agente solo es fiable si se puede comprobar. Por eso enseñamos las
  herramientas usadas y comparamos con SQL calculado aparte.

**Cierre:** "Siguiente paso: conectar el stock real y los plazos de proveedor para pasar
de detectar caídas a anticipar roturas."

---

## 10 preguntas difíciles del profesor (con respuesta corta)

1. **¿Por qué el 80 %?**
   Es el corte clásico de Pareto, fácil de explicar y de verificar. Además se cumple en
   nuestros datos: 1.036 de 4.878 productos (~21 %) concentran el 80,02 % de la
   facturación.

2. **¿Por qué comparar con el año anterior y no con el mes anterior?**
   Las ventas son muy estacionales, con pico en Navidad. Comparar con el mes anterior
   confundiría la caída normal de enero con un problema. Usamos sep-nov porque los datos
   acaban el 9-dic-2011, así que sep-nov es el último trimestre completo.

3. **¿Cómo sabéis que el agente no inventa números?**
   Por tres vías:
   - Las reglas de `AGENTS.md` le obligan a usar solo cifras de herramientas y a decir
     "No tengo datos para eso" si no las tiene.
   - La app enseña el resultado bruto de cada herramienta.
   - Comprobamos sus respuestas contra SQL calculado aparte (P04, P07) y probamos
     preguntas trampa (P08, P09).

4. **¿Qué pasa si no hay stock real?**
   El dataset no trae existencias, así que medimos el riesgo con ventas, no con stock, y
   el agente no habla de roturas. En producción añadiríamos una herramienta MCP más que
   lea el stock del ERP.

5. **¿Por qué un solo agente y no varios?**
   El problema no lo necesita: un coordinador con 4 herramientas y una Skill lo resuelve.
   Varios agentes añaden puntos de fallo y coste sin mejorar el resultado.

6. **¿Qué librería de GitHub adaptasteis?**
   `modelcontextprotocol/python-sdk` (FastMCP). Con ella construimos nuestro servidor
   `retail-bi` y el cliente del agente. Tuvimos que adaptarnos al cambio de API de la
   versión 2.x.

7. **¿Por qué MCP y no dejar que el agente haga SQL directamente?**
   Por seguridad y control. El agente solo puede usar 4 consultas de lectura
   parametrizadas, así que no puede borrar ni leer lo que no debe. Además, el mismo
   servidor se puede conectar a Claude Desktop o a otro agente sin tocarlo.

8. **Un producto con -100 % de ventas, ¿está en riesgo o simplemente se ha descatalogado?**
   Es una limitación real: de los 472 productos A en riesgo, 66 no han vendido nada en
   sep-nov 2011 y pueden estar descatalogados. Por eso el agente recomienda revisar y no actúa solo. Una mejora
   sería cruzar con el catálogo activo.

9. **¿Cómo puede haber tasas de cancelación por encima del 100 %?**
   Porque se cancelan unidades que se vendieron antes de que empiecen los datos, como
   BLACK CHERRY LIGHTS: 248 canceladas frente a 243 vendidas (102 %). Antes además salía
   "D" (Discount), que no es un producto. Lo detectamos en las pruebas y lo corregimos
   filtrando los códigos que no son de producto.

10. **¿Qué haría falta para usarlo en producción?**
    - Datos actualizados automáticamente y stock y plazos de proveedor reales.
    - Usuario de base de datos de solo lectura y login en la app.
    - Plan de pago del LLM, porque la cuota gratuita se agota.
    - Pruebas automáticas y monitorización de los logs.
    - Un humano que aprueba cada acción.
