# Problema: productos clave en riesgo en retail online

## Alternativas consideradas (pensamiento divergente)

| # | Problema | Dataset | Por qué sí / por qué no |
|---|----------|---------|-------------------------|
| 1 | Clasificación ABC y alerta de productos en riesgo | Online Retail II (UCI) | Datos reales, licencia abierta, viable en 5 h |
| 2 | Cancelaciones y devoluciones | Online Retail II (UCI) | Útil pero corto; se integra como KPI del 1 |
| 3 | Retrasos de entrega y reseñas | Olist (Kaggle) | Vistoso, pero muchas tablas y es más logística |
| 4 | Previsión de demanda | Rossmann / M5 (Kaggle) | El modelo consume demasiado tiempo |
| 5 | Análisis de cesta | Instacart (Kaggle) | Dataset muy pesado y licencia restringida |

## Decisión (pensamiento convergente)

Elegimos el problema 1, sumando la tasa de cancelación del problema 2 como KPI.

Criterios: datos reales con licencia clara, una sola tabla, resultado comprobable con SQL
y viable en el tiempo del hackathon.

## Usuario

Responsable de compras de una pyme de comercio online con cientos de productos.

## Problema

No sabe de un vistazo qué productos generan la mayor parte de la facturación ni cuáles
de esos se están frenando. Lo descubre tarde, revisando hojas de cálculo a mano.

## Propuesta de valor

Un agente al que se le pregunta en lenguaje normal ("¿qué productos importantes están
cayendo?") y responde con la lista, los datos que lo justifican y una recomendación.

## Objetivos

- Identificar los productos clase A (los que suman el 80 % de la facturación).
- Detectar a tiempo los productos A con caída de ventas.
- Señalar los productos con más cancelaciones.

## KPI

| KPI | Cómo se calcula |
|-----|-----------------|
| % facturación de la clase A | Facturación de productos A / facturación total |
| Productos A en riesgo | Productos A cuyas ventas de los últimos 3 meses caen más de un 30 % frente a los mismos 3 meses del año anterior |
| Tasa de cancelación por producto | Unidades canceladas / unidades vendidas |

## Limitaciones conocidas

- El dataset no trae stock real: el riesgo se mide con ventas, no con existencias.
- Las ventas son muy estacionales (picos en Navidad), por eso comparamos con el mismo
  periodo del año anterior y no con el mes previo.
- Datos de 2009 a 2011: sirven para demostrar el método, no para decisiones actuales.
