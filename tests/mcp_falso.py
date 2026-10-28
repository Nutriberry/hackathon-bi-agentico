"""Servidor MCP falso para desarrollo sin Supabase.
Devuelve datos de ejemplo con la misma interfaz que backend/mcp_server.py.
"""
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("retail-bi-falso")


@mcp.tool()
def kpi_resumen() -> dict:
    """Resumen global de KPIs (datos de ejemplo)."""
    return {
        "facturacion_total": 8187806.36,
        "n_productos": 3684,
        "n_productos_a": 213,
        "pct_facturacion_a": 0.8003,
    }


@mcp.tool()
def productos_en_riesgo(umbral_caida: float = 0.30, limite: int = 10) -> list[dict]:
    """Productos clase A con mayor caída (datos de ejemplo)."""
    return [
        {
            "stock_code": "84029E",
            "description": "RED RETROSPOT PENNY FARTHING",
            "ventas_2010": 1200.00,
            "ventas_2011": 480.00,
            "variacion_pct": -0.60,
        },
        {
            "stock_code": "22197",
            "description": "SMALL POPCORN HOLDER",
            "ventas_2010": 980.00,
            "ventas_2011": 490.00,
            "variacion_pct": -0.50,
        },
    ]


@mcp.tool()
def tasa_cancelacion(min_unidades: int = 100, limite: int = 10) -> list[dict]:
    """Productos con mayor tasa de cancelación (datos de ejemplo)."""
    return [
        {
            "stock_code": "23166",
            "description": "MEDIUM CERAMIC TOP STORAGE JAR",
            "unidades_vendidas": 74215,
            "unidades_canceladas": 52260,
            "tasa": 0.7043,
        },
        {
            "stock_code": "85099B",
            "description": "JUMBO BAG RED RETROSPOT",
            "unidades_vendidas": 47363,
            "unidades_canceladas": 11620,
            "tasa": 0.2453,
        },
    ]


@mcp.tool()
def ventas_producto(stock_code: str) -> list[dict]:
    """Serie mensual de ventas de un producto (datos de ejemplo)."""
    return [
        {"mes": "2011-01", "unidades": 300, "importe": 450.00},
        {"mes": "2011-02", "unidades": 280, "importe": 420.00},
        {"mes": "2011-03", "unidades": 150, "importe": 225.00},
    ]


if __name__ == "__main__":
    mcp.run(transport="stdio")

