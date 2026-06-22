import streamlit as st
import pandas as pd
import plotly.express as px

from agent_runner import ask_agent
from app_functions.connect_db import connect_db

st.set_page_config(
    page_title="Mongo Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Mongo Agent")

st.markdown("""
Sistema de consulta inteligente para leyes y contrataciones públicas.
""")

db = connect_db("proyectoBDA")

tab_chat, tab_dashboard = st.tabs(
    ["🤖 Chat IA", "📊 Dashboard"]
)

# ==================================================
# CHAT
# ==================================================

with tab_chat:

    with st.sidebar:

        st.header("Información")

        st.info(
            """
            Proyecto Big Data Analytics

            MongoDB + Gemini
            """
        )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.write(message["content"])

    prompt = st.chat_input(
        "Pregunta algo..."
    )

    if prompt:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):

            with st.spinner(
                "Consultando agente..."
            ):

                result = ask_agent(prompt)

                st.write(result["answer"])

                if result["tools"]:

                    with st.expander(
                        "Herramientas utilizadas"
                    ):
                        st.json(result["tools"])

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result["answer"]
            }
        )

# ==================================================
# DASHBOARD
# ==================================================

with tab_dashboard:

    st.header("📊 Dashboard Analytics")

    total_contrataciones = db.contrataciones.count_documents({})
    total_leyes = db.leyes.count_documents({})

    pipeline_total = [
        {
            "$group": {
                "_id": None,
                "total": {
                    "$sum": "$monto_contratado_total"
                }
            }
        }
    ]

    monto_total_result = list(
        db.contrataciones.aggregate(
            pipeline_total
        )
    )

    monto_total = (
        monto_total_result[0]["total"]
        if monto_total_result
        else 0
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Contrataciones",
        f"{total_contrataciones:,}"
    )

    col2.metric(
        "Leyes",
        f"{total_leyes:,}"
    )

    col3.metric(
        "Monto Total",
        f"S/ {monto_total:,.0f}"
    )

    # Contrataciones por Sector

    sector_pipeline = [
        {
            "$group": {
                "_id": "$clasificacion.sector",
                "cantidad": {
                    "$sum": 1
                }
            }
        },
        {
            "$sort": {
                "cantidad": -1
            }
        }
    ]

    sector_df = pd.DataFrame(
        list(
            db.contrataciones.aggregate(
                sector_pipeline
            )
        )
    )

    if not sector_df.empty:

        fig = px.bar(
            sector_df,
            x="_id",
            y="cantidad",
            title="Contrataciones por Sector"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # Monto por Sector

    monto_sector_pipeline = [
        {
            "$group": {
                "_id": "$clasificacion.sector",
                "monto": {
                    "$sum": "$monto_contratado_total"
                }
            }
        },
        {
            "$sort": {
                "monto": -1
            }
        }
    ]

    monto_df = pd.DataFrame(
        list(
            db.contrataciones.aggregate(
                monto_sector_pipeline
            )
        )
    )

    if not monto_df.empty:

        fig = px.bar(
            monto_df,
            x="_id",
            y="monto",
            title="Monto Contratado por Sector"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # Monedas

    moneda_pipeline = [
        {
            "$group": {
                "_id": "$moneda",
                "cantidad": {
                    "$sum": 1
                }
            }
        }
    ]

    moneda_df = pd.DataFrame(
        list(
            db.contrataciones.aggregate(
                moneda_pipeline
            )
        )
    )

    if not moneda_df.empty:

        fig = px.pie(
            moneda_df,
            names="_id",
            values="cantidad",
            title="Distribución de Monedas"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # Leyes por Sector

    leyes_pipeline = [
        {
            "$group": {
                "_id": "$sector_clasificado",
                "cantidad": {
                    "$sum": 1
                }
            }
        },
        {
            "$sort": {
                "cantidad": -1
            }
        }
    ]

    leyes_df = pd.DataFrame(
        list(
            db.leyes.aggregate(
                leyes_pipeline
            )
        )
    )

    if not leyes_df.empty:

        fig = px.bar(
            leyes_df,
            x="_id",
            y="cantidad",
            title="Leyes por Sector"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )