# 🛒 Agente BI Agéntico — Retail

Agente de inteligencia de negocio que detecta automáticamente los productos clave en riesgo de una tienda online.
Combina clasificación ABC, análisis de caída de ventas y tasa de cancelación para que cualquier responsable de compras pueda tomar decisiones en segundos, sin tocar una hoja de cálculo.
Proyecto académico desarrollado en el hackathon **Business Intelligence × IA Agéntica** de [INESDI](https://www.inesdi.com/).

---

## 1. Problema y usuario

El equipo de compras de una tienda online no tiene tiempo de revisar miles de referencias cada semana.
El agente prioriza automáticamente los productos de clase A (los que generan el 80 % de la facturación) cuyas ventas caen de forma significativa, y los que acumulan más cancelaciones.

→ Ver análisis completo en [`investigacion/problema.md`](investigacion/problema.md)

---

## 2. Arquitectura

```
Streamlit (frontend) ──► Agente Python + Gemini API (tool calling)
                                │
                    Skill: analisis-reposicion
                                │
                    Servidor MCP "retail-bi" (FastMCP)
                                │
                         Supabase / Postgres
                         (datos Online Retail II)
```

→ Diagrama detallado en [`docs/arquitectura.md`](docs/arquitectura.md)

### Componentes

| Componente | Tecnología | Función |
|---|---|---|
| Frontend | Streamlit | Interfaz de chat para el usuario |
| Agente | Python + Gemini API | Razonamiento y orquestación de herramientas |
| Skill | `skills/analisis-reposicion/` | Instrucciones de dominio para el agente |
| Servidor MCP | FastMCP (`backend/mcp_server.py`) · librería GitHub [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) | Herramientas de datos sobre ventas |
| Base de datos | Supabase (Postgres) | Almacenamiento de las transacciones |
| Datos | Online Retail II — UCI, CC BY 4.0 | Fuente de datos histórica |

---

## 3. Estructura de carpetas

```
hackathon-bi-agentico/
│
├── README.md                          # Este archivo
├── AGENTS.md                          # Instrucciones para el agente
├── CLAUDE.md                          # Notas de contexto para el LLM
├── REFLEXION.md                       # Reflexión del equipo
├── requirements.txt
├── .env.example                       # Plantilla de variables de entorno
│
├── investigacion/
│   ├── problema.md                    # Definición del problema y usuario
│   └── mercado.md
│
├── docs/
│   ├── arquitectura.md                # Diagrama y decisiones de arquitectura
│   ├── decisiones.md
│   └── prompts-equipo.md
│
├── agents/
│   └── agente.py                      # Agente principal (MCP + Gemini)
│
├── skills/
│   └── analisis-reposicion/
│       └── SKILL.md                   # Skill de dominio retail
│
├── data/
│   ├── fuente.md                      # Descripción de la fuente de datos
│   ├── perfil_datos.md                # Perfil estadístico del dataset
│   └── muestra_1000.csv               # Muestra de 1 000 filas para pruebas
│
├── backend/
│   ├── db.py                          # Conexión a Supabase
│   ├── cargar_datos.py                # Carga el Excel de UCI a Supabase
│   ├── perfilar_datos.py              # Genera el perfil estadístico
│   ├── kpi_referencia.py              # Cálculos KPI de referencia
│   └── mcp_server.py                  # Servidor MCP "retail-bi" (FastMCP)
│
├── frontend/
│   └── app.py                         # Aplicación Streamlit
│
└── tests/
    ├── pruebas.md                     # Plan de pruebas
    ├── kpi_referencia.md              # KPIs de referencia para validación
    ├── test_mcp.py                    # Prueba del servidor MCP
    ├── ejecutar_pruebas.py            # Batería de pruebas automática
    ├── evidencias/                    # Salidas y capturas de cada prueba
    └── mcp_falso.py                   # Servidor MCP con datos de ejemplo
```

---

## 4. Requisitos

- **Python 3.12** (recomendado; compatible con 3.11+)
- Cuenta gratuita en [Supabase](https://supabase.com/) (plan Free)
- Clave gratuita de [Gemini API](https://aistudio.google.com/app/apikey) (capa gratuita)

---

## 5. Instalación (Windows)

```bash
# 1. Clonar el repositorio
git clone https://github.com/Nutriberry/hackathon-bi-agentico.git
cd hackathon-bi-agentico

# 2. Crear y activar el entorno virtual
python -m venv .venv
.venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
copy .env.example .env
# Abre .env y rellena:
#   SUPABASE_DB_URL = postgresql://...   (connection string de tu proyecto Supabase)
#   LLM_API_KEY     = ...                (tu clave de Gemini API)
#   LLM_MODEL       = gemini-flash-lite-latest  (modelo de Gemini; cámbialo si Google lo retira)
```

---

## 6. Carga de datos

1. Descarga el fichero **Online Retail II** desde [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/502/online+retail+ii) y guárdalo en `data/raw/`.
2. Ejecuta la carga:

```bash
python backend/cargar_datos.py
```

Esto crea la tabla `ventas` en tu proyecto Supabase y la puebla con los datos históricos (2009-2011).

---

## 7. Ejecución

```bash
# Probar el servidor MCP directamente
python tests/test_mcp.py

# Probar el agente en consola
python agents/agente.py

# Lanzar la aplicación completa
streamlit run frontend/app.py
```

---

## 8. Preguntas de ejemplo

La aplicación incluye cuatro botones con preguntas predefinidas (en la barra lateral, con el interruptor en **Modo real**):

1. **Dame el resumen de KPI** → facturación total, número de productos y peso de la clase A (`kpi_resumen`).
2. **¿Qué productos importantes están cayendo?** → productos clase A con caída >30 % en sep-nov 2011 frente a sep-nov 2010 (`productos_en_riesgo`).
3. **¿Qué productos tienen más cancelaciones?** → ranking por tasa de cancelación (`tasa_cancelacion`).
4. **¿Qué recomiendas reponer o revisar?** → sigue la Skill `analisis-reposicion` y cruza las tres herramientas.

También se puede escribir libremente, por ejemplo: *"¿Cómo han ido las ventas del producto 85123A?"* (`ventas_producto`).
Debajo de cada respuesta, el desplegable **"Cómo lo ha calculado"** muestra la herramienta usada y los datos exactos.

---

## 9. Pruebas

El plan de pruebas, los casos de prueba y los KPIs de referencia están documentados en:

- [`tests/pruebas.md`](tests/pruebas.md) — Plan completo de pruebas
- [`tests/kpi_referencia.md`](tests/kpi_referencia.md) — Valores esperados para validación

Para ejecutar la batería automática (P01–P09 y P12) y regenerar las evidencias:

```bash
python tests/ejecutar_pruebas.py
```

Las pruebas P10 y P11 (pantalla) se validan a mano con capturas en `tests/evidencias/`.

---

## 10. Limitaciones conocidas

- **Sin datos de stock en tiempo real**: el dataset no incluye inventario actual, por lo que el agente detecta riesgo basándose en la caída de ventas históricas, no en el stock disponible.
- **Datos históricos (2009-2011)**: el análisis se basa en el dataset Online Retail II; no es extrapolable directamente a otro periodo sin recargar datos.
- **Cuota gratuita de Gemini API**: en uso intensivo puede alcanzarse el límite por minuto (429) o el servicio puede estar saturado (503). El agente reintenta 3 veces y, si sigue fallando, muestra un mensaje claro en lugar de inventar datos.
- **Códigos que no son productos**: el dataset incluye líneas como `D` (descuentos) o `POST` (envíos). Se excluyen con el filtro de productos reales (código que empieza por 5 cifras).
- **Caídas del -100 %**: muchos productos "en riesgo" no vendieron nada en 2011; probablemente están descatalogados más que en caída.
- **Cancelaciones atípicas**: algunos productos lideran el ranking por un único pedido gigante anulado o por tasas >100 % (cancelaciones de compras anteriores a dic-2009, fuera del dataset).

---

## 11. Equipo

Proyecto desarrollado por:

- Rafael Celis
- María José Girón
- Giancarlo De las Casas
- Angello Pequeño

> ⚠️ **Seguridad**: el fichero `.env` (que contiene las claves de API y la cadena de conexión a la base de datos) está incluido en `.gitignore` y **nunca se sube al repositorio**. Usa `.env.example` como plantilla.

---

*Hackathon BI × IA Agéntica — INESDI · 2026*
