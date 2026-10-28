---
name: analisis-reposicion
description: Analiza qué productos clave están en riesgo y recomienda qué reponer o revisar.
---

Sigue este procedimiento en pasos numerados para realizar el análisis de reposición:

1. **Obtener contexto general:** Ejecuta la herramienta `kpi_resumen` para conocer las cifras globales de ventas del periodo y encuadrar el análisis.

2. **Identificar productos en riesgo:** Ejecuta la herramienta `productos_en_riesgo` para obtener el listado de productos clase A cuyas ventas de sep-nov 2011 caen más de un 30 % frente a sep-nov 2010.

3. **Evaluar cancelaciones:** Ejecuta la herramienta `tasa_cancelacion` con `limite=50` (la herramienta no filtra por producto, devuelve el ranking) y cruza por `stock_code` con la lista de productos en riesgo. Se considera **alta cancelación** si el producto aparece en ese ranking con `tasa` igual o mayor que 0,10 (10 %).

4. **Aplicar reglas de recomendación:**
   * **Riesgo + Alta tasa de cancelación:** Recomendar *"revisar calidad o proveedor"* (indica posibles defectos de fábrica o descripciones erróneas).
   * **Riesgo + Sin cancelaciones altas:** Recomendar *"reducir reposición o lanzar promoción"* (indica baja demanda o falta de rotación comercial).

5. **Formato de salida:**
   * **Resumen inicial:** Un texto breve de máximo 3 líneas con la situación general.
   * **Tabla de productos:** Una tabla que desglose los productos analizados, variación de ventas, tasa de cancelación (o "sin datos") y acción recomendada.
   * **Recomendaciones detalladas:** Lista explicativa con la acción recomendada por producto, citando siempre los números exactos reportados por las herramientas.