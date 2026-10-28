"""Calcula los 3 KPI de referencia con SQL directo contra Supabase.

Excluye siempre cancelaciones (es_cancelacion) y filas con price <= 0.
Estos valores son la referencia contra la que se validará al agente.
"""
import os

import psycopg2
from dotenv import load_dotenv

RUTA_SALIDA = "tests/kpi_referencia.md"

FILTRO_BASE = "NOT es_cancelacion AND price > 0"
# Códigos que no son productos reales (envío, comisiones, descuentos, ajustes,
# pruebas, tarjetas regalo...) distorsionan el ABC y el ranking de cancelación.
# Los productos reales siempre tienen stock_code de 5 cifras al inicio.
FILTRO_PRODUCTO_REAL = "stock_code ~ '^[0-9]{5}'"

SQL_ABC = f"""
-- Facturación por producto (sin cancelaciones ni price<=0)
WITH facturacion_producto AS (
    SELECT stock_code, SUM(importe) AS facturacion
    FROM ventas
    WHERE {FILTRO_BASE} AND {FILTRO_PRODUCTO_REAL}
    GROUP BY stock_code
),
-- Ordenamos de mayor a menor y acumulamos el % de facturación (curva de Pareto)
acumulado AS (
    SELECT
        stock_code,
        facturacion,
        SUM(facturacion) OVER (ORDER BY facturacion DESC) AS facturacion_acumulada,
        SUM(facturacion) OVER () AS facturacion_total
    FROM facturacion_producto
)
SELECT
    stock_code,
    facturacion,
    facturacion_acumulada / facturacion_total AS pct_acumulado
FROM acumulado
ORDER BY facturacion DESC;
"""

SQL_PRODUCTOS_RIESGO = f"""
-- Clase A: productos que, ordenados por facturación, suman hasta el 80% del total
WITH facturacion_producto AS (
    SELECT stock_code, SUM(importe) AS facturacion
    FROM ventas
    WHERE {FILTRO_BASE} AND {FILTRO_PRODUCTO_REAL}
    GROUP BY stock_code
),
acumulado AS (
    SELECT
        stock_code,
        facturacion,
        SUM(facturacion) OVER (ORDER BY facturacion DESC) AS facturacion_acumulada,
        SUM(facturacion) OVER () AS facturacion_total
    FROM facturacion_producto
),
clase_a AS (
    SELECT stock_code
    FROM acumulado
    WHERE (facturacion_acumulada - facturacion) / facturacion_total < 0.8
),
-- Ventas de cada producto A en sep-nov 2011 vs sep-nov 2010
ventas_2011 AS (
    SELECT stock_code, SUM(importe) AS facturacion_2011
    FROM ventas
    WHERE {FILTRO_BASE} AND {FILTRO_PRODUCTO_REAL} AND invoice_date >= '2011-09-01' AND invoice_date < '2011-12-01'
    GROUP BY stock_code
),
ventas_2010 AS (
    SELECT stock_code, SUM(importe) AS facturacion_2010
    FROM ventas
    WHERE {FILTRO_BASE} AND {FILTRO_PRODUCTO_REAL} AND invoice_date >= '2010-09-01' AND invoice_date < '2010-12-01'
    GROUP BY stock_code
)
SELECT
    a.stock_code,
    COALESCE(v10.facturacion_2010, 0) AS facturacion_2010,
    COALESCE(v11.facturacion_2011, 0) AS facturacion_2011,
    (COALESCE(v11.facturacion_2011, 0) - v10.facturacion_2010) / v10.facturacion_2010 AS variacion
FROM clase_a a
JOIN ventas_2010 v10 ON v10.stock_code = a.stock_code
LEFT JOIN ventas_2011 v11 ON v11.stock_code = a.stock_code
WHERE v10.facturacion_2010 > 0
  AND (COALESCE(v11.facturacion_2011, 0) - v10.facturacion_2010) / v10.facturacion_2010 < -0.3
ORDER BY variacion ASC;
"""

SQL_TOP_CANCELACION = f"""
-- Tasa de cancelación = unidades canceladas / unidades vendidas, min. 100 unidades vendidas
WITH vendidas AS (
    SELECT stock_code, SUM(quantity) AS unidades_vendidas
    FROM ventas
    WHERE {FILTRO_BASE} AND {FILTRO_PRODUCTO_REAL}
    GROUP BY stock_code
    HAVING SUM(quantity) >= 100
),
canceladas AS (
    SELECT stock_code, SUM(ABS(quantity)) AS unidades_canceladas
    FROM ventas
    WHERE es_cancelacion AND {FILTRO_PRODUCTO_REAL}
    GROUP BY stock_code
)
SELECT
    v.stock_code,
    v.unidades_vendidas,
    COALESCE(c.unidades_canceladas, 0) AS unidades_canceladas,
    COALESCE(c.unidades_canceladas, 0)::numeric / v.unidades_vendidas AS tasa_cancelacion
FROM vendidas v
LEFT JOIN canceladas c ON c.stock_code = v.stock_code
ORDER BY tasa_cancelacion DESC
LIMIT 10;
"""


def pct_facturacion_clase_a(conn):
    with conn.cursor() as cur:
        cur.execute(SQL_ABC)
        filas = cur.fetchall()
    # % de facturación de clase A = el % acumulado justo donde se cruza el 80%
    for stock_code, facturacion, pct_acumulado in filas:
        if pct_acumulado >= 0.8:
            return float(pct_acumulado)
    return None


def productos_a_en_riesgo(conn):
    with conn.cursor() as cur:
        cur.execute(SQL_PRODUCTOS_RIESGO)
        return cur.fetchall()


def top_cancelacion(conn):
    with conn.cursor() as cur:
        cur.execute(SQL_TOP_CANCELACION)
        return cur.fetchall()


def main():
    load_dotenv()
    conn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
    try:
        pct_a = pct_facturacion_clase_a(conn)
        riesgo = productos_a_en_riesgo(conn)
        top_cancel = top_cancelacion(conn)

        with open(RUTA_SALIDA, "w", encoding="utf-8") as f:
            f.write("# KPI de referencia\n\n")
            f.write("Excluye siempre cancelaciones (`es_cancelacion`) y filas con `price <= 0`.\n\n")

            f.write("## 1. % de facturación de la clase A\n\n")
            f.write(f"**{pct_a:.2%}**\n\n")
            f.write("```sql\n" + SQL_ABC.strip() + "\n```\n\n")

            f.write("## 2. Productos A en riesgo (ventas sep-nov 2011 caen >30% vs sep-nov 2010)\n\n")
            f.write(f"**{len(riesgo)} productos en riesgo**\n\n")
            f.write("| stock_code | facturación 2010 | facturación 2011 | variación |\n|---|---|---|---|\n")
            for stock_code, fact_2010, fact_2011, var in riesgo:
                f.write(f"| {stock_code} | {fact_2010:.2f} | {fact_2011:.2f} | {var:.2%} |\n")
            f.write("\n```sql\n" + SQL_PRODUCTOS_RIESGO.strip() + "\n```\n\n")

            f.write("## 3. Top 10 productos por tasa de cancelación (mín. 100 unidades vendidas)\n\n")
            f.write("| stock_code | unidades vendidas | unidades canceladas | tasa |\n|---|---|---|---|\n")
            for stock_code, vendidas, canceladas, tasa in top_cancel:
                f.write(f"| {stock_code} | {vendidas} | {canceladas} | {tasa:.2%} |\n")
            f.write("\n```sql\n" + SQL_TOP_CANCELACION.strip() + "\n```\n")

        print(f"% facturación clase A: {pct_a:.2%}")
        print(f"Productos A en riesgo: {len(riesgo)}")
        print(f"Top cancelación calculado: {len(top_cancel)} filas")
        print(f"Guardado en {RUTA_SALIDA}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
