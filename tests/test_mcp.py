"""Arranca backend/mcp_server.py como proceso y lo prueba como cliente MCP real
(stdio), listando sus herramientas y llamando a cada una con datos de ejemplo."""
import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PARAMS = StdioServerParameters(command=sys.executable, args=["backend/mcp_server.py"])


async def main():
    async with stdio_client(PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            herramientas = await session.list_tools()
            print("Herramientas disponibles:", [t.name for t in herramientas.tools])

            llamadas = [
                ("kpi_resumen", {}),
                ("productos_en_riesgo", {"umbral_caida": 0.30, "limite": 5}),
                ("tasa_cancelacion", {"min_unidades": 100, "limite": 5}),
                ("ventas_producto", {"stock_code": "85048"}),
            ]
            for nombre, args in llamadas:
                resultado = await session.call_tool(nombre, args)
                # Si la herramienta devuelve una lista, MCP manda un bloque de
                # contenido por elemento; si devuelve un dict, manda uno solo.
                valores = [json.loads(bloque.text) for bloque in resultado.content]
                salida = valores if len(valores) != 1 else valores[0]
                print(f"\n--- {nombre}({args}) ---")
                print(json.dumps(salida, indent=2, ensure_ascii=False)[:1500])


if __name__ == "__main__":
    asyncio.run(main())
