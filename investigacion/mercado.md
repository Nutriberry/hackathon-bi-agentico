# Investigación de Mercado: Detección de Productos Clave en Riesgo y Clasificación ABC en Retail Online

## 1. Resolución actual del problema por las empresas

Las empresas de retail online gestionan la clasificación de inventario (ABC) y los riesgos de stockout mediante tres métodos principales:

- **Hojas de cálculo manuales (Excel/Google Sheets)**: exportación periódica de datos de ventas e inventario para calcular el análisis Pareto (80% ingresos = Clase A). Método reactivo, propenso a errores humanos y obsoleto al instante.
- **Módulos integrados de ERP/WMS**: sistemas como SAP, NetSuite o Microsoft Dynamics aplican reglas estáticas programadas (ej. recálculo trimestral o anual de categorías ABC según volumen de ventas histórico).
- **Sistemas dedicados de Inventory Planning (SaaS)**: herramientas avanzadas que combinan datos de ventas en tiempo real con tiempos de entrega de proveedores (lead time) para calcular puntos de reorden y clasificar automáticamente el catálogo.

## 2. Herramientas y competidores principales

| Herramienta | Enlace | Foco principal |
|---|---|---|
| Slimstock (Slim4) | slimstock.com | Optimización de inventario empresarial y clasificación ABC/XYZ avanzada. |
| Inventory Planner | inventory-planner.com | Planificación de demanda y reabastecimiento enfocado en e-commerce. |
| ToolsGroup | toolsgroup.com | Previsión probabilística de demanda y optimización multi-escalón para retail. |
| Cin7 (Inventoro) | cin7.com | Previsión de demanda basada en IA y gestión integral de inventario multicanal. |

## 3. Limitaciones de las soluciones actuales

- **Reglas estáticas e inflexibles**: la clasificación ABC tradicional mira solo ingresos o margen histórico. Un producto "C" que se convierte en tendencia viral en redes sociales no se promociona a "A" hasta que el daño por falta de stock ya ha ocurrido.
- **Ceguera ante factores externos**: las alertas de stockout se basan puramente en la velocidad de venta histórica, ignorando estacionalidad, promociones del marketing, cambios de precios de la competencia o retrasos en la cadena de suministro.
- **Fatiga de alertas y dashboards pasivos**: los dashboards clásicos muestran el problema cuando ya existe o saturan al usuario con cientos de alertas genéricas sin priorización clara de impacto financiero.

## 4. Agente de IA vs. dashboard clásico

| Dimensión | Dashboard clásico | Agente de IA proactivo |
|---|---|---|
| Monitoreo | Pasivo (requiere que el usuario entre y filtre la información). | Activo/continuo (evalúa el catálogo 24/7 en segundo plano). |
| Contexto de clasificación | Basado únicamente en histórico interno (ej. ventas de los últimos 90 días). | Dinámico y multivariable (combina ventas, elasticidad, tendencia exterior y lead times). |
| Detección de riesgo | Umbrales fijos (ej. alertar cuando queden < 10 unidades). | Previsión probabilística (anticipa roturas antes de que el nivel de stock baje del límite). |
| Acción y recomendación | Muestra datos; la decisión y ejecución es 100% manual. | Sugiere la orden de compra exacta e incluso redacta o ejecuta el reorden previa aprobación. |

## 5. Fuentes

- NetSuite - ABC Inventory Management Guide
- Slimstock - ABC Analysis & Inventory Optimization
- Inventory Planner - Prioritizing Inventory Replenishment
- ToolsGroup - Intermittent Demand Forecasting & Stockout Risk
