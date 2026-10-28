# Registro de decisiones

Cada decisión en una línea, con su porqué. Sirve para la defensa y para REFLEXION.md.

| # | Fase | Decisión | Por qué |
|---|------|----------|---------|
| 1 | Preparación | Stack: Python + Supabase + FastMCP + Streamlit + GitHub | Lenguaje del curso, BD real en la nube, MCP oficial en Python y frontend sin escribir HTML |
| 2 | Preparación | Un solo agente coordinador | Cumple el requisito y reduce puntos de fallo en 5 h |
| 3 | Preparación | MCP propio con FastMCP (repo modelcontextprotocol/python-sdk) | Es MCP real y además cuenta como librería de GitHub adaptada |
| 4 | Preparación | Claves solo en .env; en el repo solo .env.example | Requisito de la entrega: no subir credenciales |
| 5 | Investigación | Sector retail / inventario | Experiencia previa del equipo y muchos datasets reales disponibles |
| 6 | Investigación | Problema 1: ABC y productos clave en riesgo (+ cancelaciones como KPI) | Datos reales, licencia clara, una tabla, comprobable con SQL y viable en el tiempo |
| 7 | Investigación | Corte ABC al 80 % de la facturación | Criterio clásico de Pareto, fácil de explicar y verificar |
| 8 | Investigación | Comparar con el mismo periodo del año anterior | Evita confundir la caída normal tras Navidad con un problema real |
