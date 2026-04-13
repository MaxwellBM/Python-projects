"""
dashboard.py — Dashboard interactivo con Streamlit que consume la FastAPI
"""

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Data Pipeline Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estilos ───────────────────────────────────────────────────────────────────

st.markdown("""
<style>
.metric-card {
    background: #f0f4ff;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    border-left: 4px solid #4F6BED;
}
.metric-value { font-size: 2rem; font-weight: 700; color: #1a237e; }
.metric-label { font-size: 0.85rem; color: #666; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def fetch(endpoint: str, params: dict = None):
    try:
        r = requests.get(f"{API_URL}{endpoint}", params=params, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.ConnectionError:
        st.error("❌ No se puede conectar a la API. Asegúrate de que esté corriendo: `uvicorn src.api:app`")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("📊 Data Dashboard")
    st.caption("Pipeline ETL — Quotes Dataset")
    st.divider()

    health = fetch("/health")
    if health:
        status = health.get("status", "unknown")
        color = "🟢" if status == "healthy" else "🟡"
        st.markdown(f"**API Status:** {color} {status}")
        st.caption(f"DB: {health.get('database', 'N/A')}")
    else:
        st.markdown("**API Status:** 🔴 offline")

    st.divider()
    page = st.radio("Navegar", ["Resumen", "Quotes", "Autores", "Tags", "Buscar"])


# ── Página: Resumen ───────────────────────────────────────────────────────────

if page == "Resumen":
    st.title("📈 Resumen del Dataset")

    summary = fetch("/summary")
    if summary:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Quotes", summary["total_quotes"])
        with col2:
            st.metric("Autores únicos", summary["unique_authors"])
        with col3:
            st.metric("Palabras promedio", summary["avg_word_count"])
        with col4:
            st.metric("Autor top", summary["top_author"])

    st.subheader("Top autores")
    authors_data = fetch("/authors", {"limit": 10})
    if authors_data:
        df = pd.DataFrame(authors_data)
        fig = px.bar(
            df, x="quote_count", y="author", orientation="h",
            color="quote_count", color_continuous_scale="Blues",
            labels={"quote_count": "Quotes", "author": "Autor"},
        )
        fig.update_layout(showlegend=False, height=400, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Tags más frecuentes")
    tags_data = fetch("/tags", {"limit": 12})
    if tags_data:
        df_tags = pd.DataFrame(tags_data)
        fig2 = px.treemap(df_tags, path=["tag"], values="count", color="count",
                          color_continuous_scale="Teal")
        fig2.update_layout(height=350)
        st.plotly_chart(fig2, use_container_width=True)


# ── Página: Quotes ────────────────────────────────────────────────────────────

elif page == "Quotes":
    st.title("💬 Quotes")

    col1, col2 = st.columns([3, 1])
    with col1:
        author_filter = st.text_input("Filtrar por autor", placeholder="Ej: Einstein")
    with col2:
        limit = st.selectbox("Mostrar", [10, 25, 50], index=0)

    params = {"limit": limit}
    if author_filter:
        params["author"] = author_filter

    data = fetch("/quotes", params)
    if data:
        df = pd.DataFrame(data)
        st.dataframe(
            df[["author", "text", "tags", "word_count", "length_category"]],
            use_container_width=True,
            hide_index=True,
        )
        st.caption(f"{len(df)} quotes mostradas")


# ── Página: Autores ───────────────────────────────────────────────────────────

elif page == "Autores":
    st.title("👤 Estadísticas por Autor")

    data = fetch("/authors", {"limit": 20})
    if data:
        df = pd.DataFrame(data)
        fig = px.scatter(
            df, x="avg_words", y="quote_count", text="author",
            size="quote_count", color="avg_words",
            color_continuous_scale="Viridis",
            labels={"avg_words": "Palabras promedio", "quote_count": "Nº de quotes"},
        )
        fig.update_traces(textposition="top center")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df, use_container_width=True, hide_index=True)


# ── Página: Tags ──────────────────────────────────────────────────────────────

elif page == "Tags":
    st.title("🏷️ Análisis de Tags")

    data = fetch("/tags", {"limit": 20})
    if data:
        df = pd.DataFrame(data)
        fig = px.pie(df, names="tag", values="count", hole=0.4,
                     color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True, hide_index=True)


# ── Página: Buscar ────────────────────────────────────────────────────────────

elif page == "Buscar":
    st.title("🔍 Buscar Quotes")

    query = st.text_input("Buscar en quotes o autores", placeholder="Ej: imagination")
    if query and len(query) >= 2:
        data = fetch("/search", {"q": query, "limit": 10})
        if data:
            st.success(f"{len(data)} resultado(s) encontrado(s)")
            for item in data:
                with st.expander(f"**{item['author']}** — {item['word_count']} palabras"):
                    st.write(f"_{item['text']}_")
                    st.caption(f"Tags: {item['tags']}")
        else:
            st.info("Sin resultados.")
    elif query:
        st.warning("Escribe al menos 2 caracteres.")
