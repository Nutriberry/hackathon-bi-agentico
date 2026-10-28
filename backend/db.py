"""Acceso a la base de datos Supabase para el servidor MCP."""
import os
from pathlib import Path

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# Ruta absoluta al .env del proyecto: así funciona sin importar desde qué
# directorio de trabajo se lance el proceso (ej. Claude Desktop/Code).
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def consultar(sql: str, params: tuple = ()) -> list[dict]:
    """Ejecuta `sql` con `params` (siempre parametrizado, nunca concatenar texto) y
    devuelve una lista de diccionarios, una por fila."""
    conn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            return [dict(fila) for fila in cur.fetchall()]
    finally:
        conn.close()
