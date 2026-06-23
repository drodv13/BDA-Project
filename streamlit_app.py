import streamlit as st
import pandas as pd
import plotly.express as px
import PyPDF2

from docx import Document

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


def read_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return ""

    file_content = ""

    if uploaded_file.type == "text/plain":
        file_content = uploaded_file.read().decode(
            "utf-8",
            errors="ignore"
        )

    elif uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)

        for page in pdf_reader.pages:
            file_content += page.extract_text() or ""

    elif uploaded_file.type in [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword"
    ]:
        doc = Document(uploaded_file)

        for paragraph in doc.paragraphs:
            file_content += paragraph.text + "\n"

    return file_content


def get_year_filters(selected_year):
    if selected_year == "Todos":
        return {}, {}

    contrataciones_match = {
        "$or": [
            {
                "publicacion": {
                    "$regex": selected_year
                }
            },
            {
                "publicacion.fecha_publicacion": {
                    "$regex": selected_year
                }
            },
            {
                "vigencia.fecha_suscripcion": {
                    "$regex": selected_year
                }
            },
            {
                "vigencia.fecha_inicio": {
                    "$regex": selected_year
                }
            },
            {
                "vigencia.fecha_fin": {
                    "$regex": selected_year
                }
            }
        ]
    }

    leyes_match = {
        "publicacion": {
            "$regex": selected_year
        }
    }

    return contrataciones_match, leyes_match


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

        uploaded_file = st.file_uploader(
            "📄 Sube un archivo para consultarlo",
            type=["pdf", "docx", "txt"]
        )

        if "document_content" not in st.session_state:
            st.session_state.document_content = ""

        if uploaded_file:
            st.success(f"Archivo cargado: {uploaded_file.name}")

            st.session_state.document_content = read_uploaded_file(
                uploaded_file
            )

            st.caption(
                f"Texto extraído: {len(st.session_state.document_content):,} caracteres"
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

                try:
                    result = ask_agent(
                        prompt,
                        st.session_state.document_content
                    )

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

                except Exception as e:
                    st.error(
                        "El servicio de IA está temporalmente ocupado o hubo un problema procesando la consulta. Intenta nuevamente."
                    )
                    st.exception(e)


# ==================================================
# DASHBOARD
# ==================================================

with tab_dashboard:

    st.header("📊 Dashboard Analytics")

    st.subheader("Filtro")

    selected_year = st.selectbox(
        "Selecciona un año",
        ["Todos", "2020", "2021", "2022", "2023", "2024", "2025"]
    )

    contrataciones_match, leyes_match = get_year_filters(selected_year)

    total_contrataciones = db.contrataciones.count_documents(
        contrataciones_match
    )

    total_leyes = db.leyes.count_documents(
        leyes_match
    )

    pipeline_total = []

    if contrataciones_match:
        pipeline_total.append(
            {
                "$match": contrataciones_match
            }
        )

    pipeline_total.append(
        {
            "$group": {
                "_id": None,
                "total": {
                    "$sum": "$monto_contratado_total"
                }
            }
        }
    )

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

    # -----------------------------
    # Contrataciones por Sector
    # -----------------------------

    sector_pipeline = []

    if contrataciones_match:
        sector_pipeline.append(
            {
                "$match": contrataciones_match
            }
        )

    sector_pipeline.extend(
        [
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
    )

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

    # -----------------------------
    # Monto por Sector
    # -----------------------------

    monto_sector_pipeline = []

    if contrataciones_match:
        monto_sector_pipeline.append(
            {
                "$match": contrataciones_match
            }
        )

    monto_sector_pipeline.extend(
        [
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
    )

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

    # -----------------------------
    # Leyes por Sector
    # -----------------------------

    leyes_pipeline = []

    if leyes_match:
        leyes_pipeline.append(
            {
                "$match": leyes_match
            }
        )

    leyes_pipeline.extend(
        [
            {
                "$group": {
                    "_id": "$sector_clasificado",
                    "cantidad_leyes": {
                        "$sum": 1
                    }
                }
            },
            {
                "$sort": {
                    "cantidad_leyes": -1
                }
            }
        ]
    )

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
            y="cantidad_leyes",
            title="Leyes por Sector"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # -----------------------------
    # Scatter / Bubble Plot
    # -----------------------------

    st.subheader("Relación entre Leyes, Contrataciones y Monto")

    contrataciones_sector_pipeline = []

    if contrataciones_match:
        contrataciones_sector_pipeline.append(
            {
                "$match": contrataciones_match
            }
        )

    contrataciones_sector_pipeline.extend(
        [
            {
                "$group": {
                    "_id": "$clasificacion.sector",
                    "numero_contrataciones": {
                        "$sum": 1
                    },
                    "monto_total": {
                        "$sum": "$monto_contratado_total"
                    }
                }
            }
        ]
    )

    leyes_sector_pipeline = []

    if leyes_match:
        leyes_sector_pipeline.append(
            {
                "$match": leyes_match
            }
        )

    leyes_sector_pipeline.extend(
        [
            {
                "$group": {
                    "_id": "$sector_clasificado",
                    "numero_leyes": {
                        "$sum": 1
                    }
                }
            }
        ]
    )

    contrataciones_sector_df = pd.DataFrame(
        list(
            db.contrataciones.aggregate(
                contrataciones_sector_pipeline
            )
        )
    )

    leyes_sector_df = pd.DataFrame(
        list(
            db.leyes.aggregate(
                leyes_sector_pipeline
            )
        )
    )

    if (
        not contrataciones_sector_df.empty
        and not leyes_sector_df.empty
    ):

        scatter_df = pd.merge(
            leyes_sector_df,
            contrataciones_sector_df,
            on="_id",
            how="outer"
        )

        scatter_df["numero_leyes"] = scatter_df["numero_leyes"].fillna(0)
        scatter_df["numero_contrataciones"] = scatter_df["numero_contrataciones"].fillna(0)
        scatter_df["monto_total"] = scatter_df["monto_total"].fillna(0)

        scatter_df = scatter_df.rename(
            columns={
                "_id": "sector"
            }
        )

        fig = px.scatter(
            scatter_df,
            x="numero_leyes",
            y="numero_contrataciones",
            size="monto_total",
            hover_name="sector",
            hover_data={
                "numero_leyes": True,
                "numero_contrataciones": True,
                "monto_total": ":,.0f"
            },
            title="Número de Leyes vs Número de Contrataciones por Sector",
            labels={
                "numero_leyes": "Número de leyes",
                "numero_contrataciones": "Número de contrataciones",
                "monto_total": "Monto contratado"
            },
            size_max=60
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        with st.expander("Ver datos del scatter plot"):
            st.dataframe(
                scatter_df,
                use_container_width=True
            )

    else:

        st.warning(
            "No hay datos suficientes para construir el scatter plot con el filtro seleccionado."
        )
