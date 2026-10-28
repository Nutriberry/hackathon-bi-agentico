# Reflexión del equipo

Hackathon INESDI · Business Intelligence × IA agéntica · 28/10/2026

Equipo: Giancarlo De las Casas, María José Girón, Angello Pequeño y Rafael Celis.

---

## Reflexión individual

### Giancarlo De las Casas · Coordinación, datos y servidor MCP

**1. ¿Qué he aprendido hoy?**
Que un sistema agéntico es más que el modelo: lo que lo hace útil son las herramientas
que le das y los límites que le pones. He aprendido a montar un servidor MCP propio con
FastMCP sobre una base de datos real y a conectarlo a un agente. También que un agente
solo es fiable si se puede comprobar, por eso calculamos los KPI por otro camino con SQL
y los comparamos con lo que dice el agente.

**2. ¿Qué me llevo y cómo lo aplicaré?**
Me llevo la forma de trabajar con un "contrato" entre piezas: nombres de herramientas,
parámetros y formato de salida fijados antes de programar. En mi trabajo como analista
funcional lo puedo aplicar al definir integraciones entre sistemas y al preparar casos
de prueba con valores de referencia antes de validar un desarrollo.

**3. ¿Dónde me he bloqueado y cómo lo he afrontado?**
Me bloqueé con cosas que no dependían de nuestra lógica: la librería MCP 2.x había
cambiado nombres, el modelo de Gemini que usábamos estaba retirado y Google devolvía
errores 503. Además, un cambio mío en el agente se perdió al pisarse con otro proceso.
Lo afronté leyendo el log en lugar de suponer, separando "fallo nuestro" de "fallo
externo" y añadiendo reintentos y mensajes de error claros.

**4. ¿Qué he aportado al equipo?**
La coordinación: el plan por fases, el contrato común para que los cuatro trabajáramos
en paralelo y la integración de todas las piezas en un solo repositorio. También la
carga del dataset en Supabase, el servidor MCP y la ejecución de la batería de pruebas
con evidencias.

**5. ¿Qué haría diferente la próxima vez?**
Fijar desde el principio versiones de librerías y un modelo concreto de LLM, y ejecutar
las pruebas antes, no al final. Y revisar los resultados con ojo de negocio desde la
primera consulta real: así habríamos visto antes los códigos que no eran productos.

---

### María José Girón · Investigación, documentación y diseño del agente

**1. ¿Qué he aprendido hoy?**
He aprendido a documentar un sistema agéntico por partes: la arquitectura, las reglas
del agente (AGENTS.md) y el procedimiento de la Skill. Y que la documentación no es un
adorno: el agente lee AGENTS.md y SKILL.md, así que un error en el texto es un error en
el comportamiento.

**2. ¿Qué me llevo y cómo lo aplicaré?**
Me llevo la costumbre de revisar lo que genera la IA contra la realidad antes de darlo
por bueno. Lo aplicaré cuando use asistentes de IA para redactar informes o
especificaciones: usarlos para el borrador, pero verificar datos, nombres y cifras.

**3. ¿Dónde me he bloqueado y cómo lo he afrontado?**
Al copiar desde Google Docs, los tres archivos me salieron con el mismo contenido y con
símbolos raros que rompían el diagrama. Además, Gemini inventó una herramienta que no
existía (`clasificacion_abc`). Lo resolví pidiendo cada archivo por separado, en texto
plano, y contrastándolo con las herramientas reales del servidor.

**4. ¿Qué he aportado al equipo?**
La investigación de mercado, la documentación del dataset con los números reales del
perfil de datos, el diagrama de arquitectura, AGENTS.md, la Skill de reposición y la
plantilla de la batería de pruebas.

**5. ¿Qué haría diferente la próxima vez?**
Trabajar directamente en archivos Markdown en lugar de pasar por un procesador de texto,
y pedir al equipo la lista exacta de herramientas antes de escribir la especificación
del agente.

---

### Angello Pequeño · Agente y README

**1. ¿Qué he aprendido hoy?**
He aprendido cómo funciona por dentro un agente con *tool calling*: el modelo no consulta
la base de datos, pide una herramienta, el código la ejecuta en el servidor MCP y le
devuelve el resultado, en un bucle con un máximo de vueltas.

**2. ¿Qué me llevo y cómo lo aplicaré?**
Me llevo la idea de empezar con un servidor falso que imita al real: pude avanzar sin
base de datos ni claves y luego cambiar al real con una sola variable. Lo aplicaré en
cualquier desarrollo que dependa de otra pieza que aún no está lista.

**3. ¿Dónde me he bloqueado y cómo lo he afrontado?**
Llegué con el reto ya empezado y tuve que entender rápido un contrato que no había
definido yo. Además, el código que generó la IA funcionaba con el servidor falso pero no
con el real: no pasaba las claves al servidor y solo leía el primer resultado de las
listas. Lo afronté apoyándome en el contrato común y en la revisión del equipo.

**4. ¿Qué he aportado al equipo?**
El agente que conecta Gemini con el servidor MCP, el servidor de pruebas con datos de
ejemplo y el README con las instrucciones de instalación y ejecución.

**5. ¿Qué haría diferente la próxima vez?**
Probar el agente contra el servidor real lo antes posible, aunque sea con una sola
pregunta, en lugar de dar por bueno lo que funciona con datos falsos.

---

### Rafael Celis · Frontend, presentación y revisión

**1. ¿Qué he aprendido hoy?**
He aprendido a construir una interfaz con Streamlit que no solo muestra la respuesta,
sino también cómo se ha calculado: qué herramienta se usó, con qué parámetros y qué
devolvió. Eso hace que el usuario pueda confiar en el resultado.

**2. ¿Qué me llevo y cómo lo aplicaré?**
Me llevo que mirar los datos con criterio de negocio encuentra errores que las pruebas
técnicas no ven. Lo aplicaré revisando siempre si un resultado "tiene sentido" antes de
presentarlo.

**3. ¿Dónde me he bloqueado y cómo lo he afrontado?**
Al revisar el repositorio vi que "Discount" salía como el producto número uno en
cancelaciones, y que las capturas del modo demo tenían cifras antiguas. No sabía si era
un fallo mío o del servidor; lo comuniqué al equipo con el dato concreto y se corrigió
en el origen.

**4. ¿Qué he aportado al equipo?**
La aplicación Streamlit con el modo demo y el modo real, la detección del fallo de los
códigos que no son productos y el guion de la presentación con las preguntas difíciles.

**5. ¿Qué haría diferente la próxima vez?**
Coordinar mejor con el equipo cuándo hacer cambios en el repositorio, para no trabajar
con versiones distintas, y revisar los datos de ejemplo cada vez que cambian los reales.

---

## Reflexión colectiva

**1. ¿Qué hemos aprendido trabajando juntos?**
Que un contrato claro entre piezas permite trabajar en paralelo. Empezamos dos y a mitad
del reto llegaron dos personas más; gracias a un documento con los nombres exactos de
herramientas, funciones y archivos, cada uno construyó su parte por separado y todo
encajó en la integración con ajustes pequeños.

**2. ¿Qué nos llevamos de esta experiencia?**
Que un sistema sencillo, con datos reales y probado vale más que uno complejo. Y que la
transparencia (mostrar qué herramienta se usó y qué devolvió) es lo que hace creíble a
un agente de BI.

**3. ¿Dónde nos hemos bloqueado y cómo lo hemos resuelto?**
En problemas de versiones y servicios externos: la librería MCP 2.x, un modelo de Gemini
retirado y errores 503 de Google. También en la calidad de los datos: había códigos que
no eran productos (descuentos, portes) que distorsionaban el ABC. Lo resolvimos leyendo
los logs, separando causas internas y externas, corrigiendo en el origen (el servidor
MCP) y dejando constancia de cada error en las pruebas.

**4. ¿Cómo hemos decidido, escuchado y cuestionado a la IA?**
Usamos la IA para generar código y documentos, pero no aceptamos nada sin comprobarlo.
Gemini inventó una herramienta en AGENTS.md y entregó tres archivos iguales; el código
generado tenía fallos que solo aparecían con datos reales. Las decisiones importantes
(el problema, el corte del 80 %, comparar con el año anterior, el filtro de productos)
las tomamos nosotros con criterios explícitos y las registramos en `docs/decisiones.md`.
Y los números del agente los validamos contra SQL calculado aparte.

**5. ¿Qué haríamos diferente si empezáramos de nuevo?**
Fijar versiones y modelo desde el principio, probar con datos reales antes, revisar los
resultados con criterio de negocio desde la primera consulta y repartir el trabajo entre
cuatro desde el inicio.

---

## Tres compromisos de mejora

- **Vamos a mantener…** el contrato común entre piezas, el registro de decisiones y la
  validación de los números del agente contra una referencia calculada aparte.
- **Vamos a cambiar…** el momento de las pruebas: probar con datos reales desde el
  principio y no solo al final, y fijar versiones de librerías y del modelo.
- **Vamos a experimentar…** con separar productos descatalogados de productos en caída,
  contar pedidos cancelados en lugar de unidades y añadir datos de stock para pasar de
  detectar caídas a anticipar roturas.
