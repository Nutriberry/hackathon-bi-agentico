"""Genera un perfil de calidad de datos y una muestra aleatoria de la tabla `ventas`."""
import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

RUTA_PERFIL = "data/perfil_datos.md"
RUTA_MUESTRA = "data/muestra_1000.csv"


def obtener_metricas(conn):
    metricas = {}
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM ventas;")
        metricas["filas_totales"] = cur.fetchone()[0]

        cur.execute("SELECT MIN(invoice_date), MAX(invoice_date) FROM ventas;")
        metricas["rango_fechas"] = cur.fetchone()

        # Nulos por columna (las de texto además cuentan vacías "")
        columnas_texto = ["invoice", "stock_code", "description", "customer_id", "country"]
        columnas_otras = ["quantity", "invoice_date", "price", "es_cancelacion", "importe"]
        nulos = {}
        for col in columnas_texto:
            cur.execute(f"SELECT COUNT(*) FROM ventas WHERE {col} IS NULL OR {col} = '';")
            nulos[col] = cur.fetchone()[0]
        for col in columnas_otras:
            cur.execute(f"SELECT COUNT(*) FROM ventas WHERE {col} IS NULL;")
            nulos[col] = cur.fetchone()[0]
        metricas["nulos_por_columna"] = nulos

        cur.execute("SELECT COUNT(*) FROM ventas WHERE quantity < 0;")
        metricas["filas_quantity_negativa"] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM ventas WHERE price <= 0;")
        metricas["filas_price_no_positivo"] = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM (
                SELECT invoice, stock_code, description, quantity, invoice_date,
                       price, customer_id, country, COUNT(*)
                FROM ventas
                GROUP BY invoice, stock_code, description, quantity, invoice_date,
                         price, customer_id, country
                HAVING COUNT(*) > 1
            ) dup;
        """)
        metricas["grupos_duplicados_exactos"] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM ventas WHERE es_cancelacion;")
        metricas["num_cancelaciones"] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(DISTINCT stock_code) FROM ventas;")
        metricas["productos_distintos"] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(DISTINCT country) FROM ventas;")
        metricas["paises_distintos"] = cur.fetchone()[0]

    return metricas


def escribir_perfil(metricas):
    with open(RUTA_PERFIL, "w", encoding="utf-8") as f:
        f.write("# Perfil de datos — tabla `ventas`\n\n")
        f.write(f"- Filas totales: {metricas['filas_totales']}\n")
        f.write(f"- Rango de fechas: {metricas['rango_fechas'][0]} a {metricas['rango_fechas'][1]}\n")
        f.write(f"- Filas con quantity negativa: {metricas['filas_quantity_negativa']}\n")
        f.write(f"- Filas con price <= 0: {metricas['filas_price_no_positivo']}\n")
        f.write(f"- Grupos de filas duplicadas exactas: {metricas['grupos_duplicados_exactos']}\n")
        f.write(f"- Número de cancelaciones: {metricas['num_cancelaciones']}\n")
        f.write(f"- Productos distintos: {metricas['productos_distintos']}\n")
        f.write(f"- Países distintos: {metricas['paises_distintos']}\n\n")
        f.write("## Nulos / vacíos por columna\n\n")
        for col, n in metricas["nulos_por_columna"].items():
            f.write(f"- {col}: {n}\n")


def guardar_muestra(conn):
    df = pd.read_sql(
        "SELECT * FROM ventas ORDER BY random() LIMIT 1000;", conn
    )
    df.to_csv(RUTA_MUESTRA, index=False)


def main():
    load_dotenv()
    conn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
    try:
        metricas = obtener_metricas(conn)
        escribir_perfil(metricas)
        guardar_muestra(conn)
        print(f"Perfil guardado en {RUTA_PERFIL}")
        print(f"Muestra guardada en {RUTA_MUESTRA}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
