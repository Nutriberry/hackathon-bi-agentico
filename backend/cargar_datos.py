"""Carga el dataset Online Retail II (Excel) a la tabla `ventas` en Supabase."""
import io
import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

RUTA_EXCEL = "data/raw/online_retail_II.xlsx"

COLUMNAS_VENTAS = [
    "invoice", "stock_code", "description", "quantity", "invoice_date",
    "price", "customer_id", "country", "es_cancelacion", "importe",
]


def leer_y_limpiar():
    # 1. Leemos las dos hojas del Excel y las unimos en un solo DataFrame
    hoja_2009_2010 = pd.read_excel(RUTA_EXCEL, sheet_name="Year 2009-2010")
    hoja_2010_2011 = pd.read_excel(RUTA_EXCEL, sheet_name="Year 2010-2011")
    df = pd.concat([hoja_2009_2010, hoja_2010_2011], ignore_index=True)

    # 2. Limpieza mínima (no borramos filas, solo normalizamos)
    # Nombres de columna en minúsculas y sin espacios (el Excel trae CamelCase, ej. "StockCode")
    df = df.rename(columns={
        "Invoice": "invoice", "StockCode": "stock_code", "Description": "description",
        "Quantity": "quantity", "InvoiceDate": "invoice_date", "Price": "price",
        "Customer ID": "customer_id", "Country": "country",
    })
    # Quitamos espacios sobrantes en la descripción del producto
    df["description"] = df["description"].astype(str).str.strip()
    # Una factura es cancelación si su código empieza con "C" (convención del dataset)
    df["es_cancelacion"] = df["invoice"].astype(str).str.startswith("C")
    # Importe de la línea = cantidad * precio unitario
    df["importe"] = df["quantity"] * df["price"]
    # customer_id viene como float (con NaN); lo pasamos a texto sin ".0" y sin perder los nulos
    df["customer_id"] = df["customer_id"].astype("Int64").astype(str).replace("<NA>", "")

    return df[COLUMNAS_VENTAS]


def crear_tabla(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                invoice text,
                stock_code text,
                description text,
                quantity int,
                invoice_date timestamp,
                price numeric,
                customer_id text,
                country text,
                es_cancelacion boolean,
                importe numeric
            );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ventas_stock_code ON ventas (stock_code);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ventas_invoice_date ON ventas (invoice_date);")
    conn.commit()


def cargar_con_copy(conn, df):
    # COPY es mucho más rápido que to_sql para ~1 millón de filas
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, header=False, na_rep="")
    buffer.seek(0)
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE ventas;")
        cur.copy_expert(
            f"COPY ventas ({', '.join(COLUMNAS_VENTAS)}) FROM STDIN WITH (FORMAT csv, NULL '')",
            buffer,
        )
    conn.commit()


def main():
    load_dotenv()
    df = leer_y_limpiar()
    print(f"Filas leídas del Excel: {len(df)}")

    conn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
    try:
        crear_tabla(conn)
        cargar_con_copy(conn, df)

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM ventas;")
            filas_bd = cur.fetchone()[0]

        print(f"Filas en Supabase: {filas_bd}")
        assert filas_bd == len(df), "El número de filas no coincide con el Excel"
        print("OK: la carga coincide con el Excel.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
