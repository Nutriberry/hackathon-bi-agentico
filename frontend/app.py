# Pantalla del agente de BI (Streamlit).
# Se arranca con: streamlit run frontend/app.py
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Añadimos la carpeta raíz al path para poder importar agents/agente.py
RAIZ = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ))

PREGUNTAS_EJEMPLO = [
    "Dame el resumen de KPI",
    "¿Qué productos importantes están cayendo?",
    "¿Qué productos tienen más cancelaciones?",
    "¿Qué recomiendas reponer o revisar?",
]


# --- Datos de ejemplo para el modo demo (sin base de datos ni claves) ---

KPI_DEMO = {
    "facturacion_total": 20972594.57,
    "n_productos": 4917,
    "n_productos_a": 1005,
    "pct_facturacion_a": 0.8002,
}

RIESGO_DEMO = [
    {"stock_code": "21069", "description": "VINTAGE BILLBOARD TEA MUG",
     "ventas_2010": 535.97, "ventas_2011": 0.0, "variacion_pct": -1.0},
    {"stock_code": "20966", "description": "SANDWICH BATH SPONGE",
     "ventas_2010": 1212.42, "ventas_2011": 0.0, "variacion_pct": -1.0},
    {"stock_code": "10002", "description": "INFLATABLE POLITICAL GLOBE",
     "ventas_2010": 1765.43, "ventas_2011": 0.0, "variacion_pct": -1.0},
    {"stock_code": "20681", "description": "PINK SPOTTY CHILDS UMBRELLA",
     "ventas_2010": 1407.45, "ventas_2011": 0.0, "variacion_pct": -1.0},
]

CANCELACION_DEMO = [
    {"stock_code": "79323B", "description": "BLACK CHERRY LIGHTS",
     "unidades_vendidas": 243, "unidades_canceladas": 248, "tasa": 1.0206},
    {"stock_code": "23843", "description": "PAPER CRAFT , LITTLE BIRDIE",
     "unidades_vendidas": 80995, "unidades_canceladas": 80995, "tasa": 1.0},
    {"stock_code": "20715", "description": "LITTLE FLOWER SHOPPER BAG",
     "unidades_vendidas": 400, "unidades_canceladas": 400, "tasa": 1.0},
    {"stock_code": "23166", "description": "MEDIUM CERAMIC TOP STORAGE JAR",
     "unidades_vendidas": 78033, "unidades_canceladas": 74494, "tasa": 0.9546},
]


def responder_falso(pregunta: str) -> dict:
    """Imita a responder() con datos de ejemplo, para probar la pantalla."""
    texto = pregunta.lower()
    herramientas = []

    if "kpi" in texto or "resumen" in texto:
        herramientas.append({"nombre": "kpi_resumen", "argumentos": {}, "resultado": KPI_DEMO})
        respuesta = ("La facturación total es de 20.972.594,57. De 4.917 productos, "
                     "1.005 son clase A y concentran el 80,0 % de la facturación.")
    elif "cancela" in texto:
        herramientas.append({"nombre": "tasa_cancelacion",
                             "argumentos": {"min_unidades": 100, "limite": 10},
                             "resultado": CANCELACION_DEMO})
        respuesta = ("Los productos con más cancelaciones son BLACK CHERRY LIGHTS (102 %), "
                     "PAPER CRAFT, LITTLE BIRDIE (100 %) y MEDIUM CERAMIC TOP STORAGE JAR (95,5 %).")
    elif "cayendo" in texto or "riesgo" in texto:
        herramientas.append({"nombre": "productos_en_riesgo",
                             "argumentos": {"umbral_caida": 0.3, "limite": 10},
                             "resultado": RIESGO_DEMO})
        respuesta = ("Hay productos clase A que no han vendido nada en sep-nov 2011, "
                     "por ejemplo INFLATABLE POLITICAL GLOBE (1.765,43 en 2010).")
    else:
        herramientas.append({"nombre": "productos_en_riesgo",
                             "argumentos": {"umbral_caida": 0.3, "limite": 10},
                             "resultado": RIESGO_DEMO})
        herramientas.append({"nombre": "tasa_cancelacion",
                             "argumentos": {"min_unidades": 100, "limite": 10},
                             "resultado": CANCELACION_DEMO})
        respuesta = ("Recomiendo revisar los productos en riesgo sin cancelaciones altas "
                     "(reducir reposición o lanzar promoción) y revisar calidad o proveedor "
                     "de los que tienen alta cancelación.")

    return {"respuesta": "(Modo demo) " + respuesta, "herramientas_usadas": herramientas}


def obtener_respuesta(pregunta: str, modo_real: bool) -> dict:
    """Llama al agente real o al falso según el interruptor."""
    if modo_real:
        # Import aquí dentro: así el modo demo funciona aunque el agente no exista aún
        from agents.agente import responder
        return responder(pregunta)
    return responder_falso(pregunta)


def mostrar_herramientas(herramientas: list):
    """Desplegable con cada herramienta usada, sus argumentos y su resultado."""
    if not herramientas:
        return
    with st.expander("Cómo lo ha calculado"):
        for h in herramientas:
            st.markdown(f"**Herramienta:** `{h['nombre']}`")
            st.markdown("Argumentos:")
            st.json(h.get("argumentos", {}))
            resultado = h.get("resultado")

            # Si la herramienta devolvió un error, lo mostramos claro
            if isinstance(resultado, dict) and "error" in resultado:
                st.error(f"La herramienta devolvió un error: {resultado['error']}")
            # Si es una lista, tabla y gráfico de barras
            elif isinstance(resultado, list) and resultado:
                df = pd.DataFrame(resultado)
                st.dataframe(df, hide_index=True)
                numericas = df.select_dtypes("number").columns
                if len(numericas) > 0:
                    # Etiquetas del eje: descripción, mes o código si existen
                    for etiqueta in ["description", "mes", "stock_code"]:
                        if etiqueta in df.columns:
                            df = df.set_index(etiqueta)
                            break
                    st.bar_chart(df[numericas[0]])
            else:
                st.json(resultado)
            st.divider()


# --- Pantalla ---

st.set_page_config(page_title="Agente de BI", page_icon="📊")
st.title("Agente de BI · Productos clave en riesgo")
st.write("Pregunta en lenguaje natural qué productos importantes (clase A) están "
         "perdiendo ventas o acumulan cancelaciones, y qué conviene reponer o revisar.")

# Barra lateral: modo y preguntas de ejemplo
with st.sidebar:
    modo = st.radio("Modo", ["Modo demo", "Modo real"])
    modo_real = modo == "Modo real"
    st.subheader("Preguntas de ejemplo")
    pregunta_boton = None
    for p in PREGUNTAS_EJEMPLO:
        if st.button(p, use_container_width=True):
            pregunta_boton = p

# Historial del chat
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for m in st.session_state.mensajes:
    with st.chat_message(m["rol"]):
        st.markdown(m["contenido"])
        mostrar_herramientas(m.get("herramientas", []))

# La pregunta viene del chat o de un botón
pregunta = st.chat_input("Escribe tu pregunta...") or pregunta_boton

if pregunta:
    st.session_state.mensajes.append({"rol": "user", "contenido": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Consultando los datos..."):
                resultado = obtener_respuesta(pregunta, modo_real)
            texto = resultado["respuesta"]
            herramientas = resultado.get("herramientas_usadas", [])
        except ModuleNotFoundError:
            texto = "El agente real aún no está disponible (falta agents/agente.py). Usa el modo demo."
            herramientas = []
            st.error(texto)
        except Exception as e:
            texto = f"Algo ha fallado al responder: {e}"
            herramientas = []
            st.error(texto)
        else:
            st.markdown(texto)
            mostrar_herramientas(herramientas)

    st.session_state.mensajes.append(
        {"rol": "assistant", "contenido": texto, "herramientas": herramientas})
