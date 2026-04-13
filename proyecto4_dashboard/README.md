# 📊 Dashboard + FastAPI — Data Pipeline Visualizer

![CI/CD](https://github.com/TU_USUARIO/data-dashboard/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?logo=streamlit)

Dashboard interactivo con backend REST que visualiza los datos generados por el pipeline ETL. Incluye CI/CD completo con deploy automático a Render en cada push a `main`.

---

## 🏗️ Arquitectura

```
Scraper ETL (Proyecto 1)
        ↓
    SQLite DB
        ↓
  FastAPI (REST API)    ←── Tests con TestClient
        ↓
 Streamlit Dashboard   ←── Visualizaciones con Plotly
        ↓
   GitHub Actions CI/CD → Deploy en Render
```

---

## 🚀 Instalación y uso local

```bash
git clone https://github.com/TU_USUARIO/data-dashboard
cd data-dashboard
pip install -r requirements.txt

# Terminal 1: levantar la API
uvicorn src.api:app --reload

# Terminal 2: levantar el dashboard
streamlit run src/dashboard.py
```

- **API:** http://localhost:8000
- **Docs automáticos:** http://localhost:8000/docs
- **Dashboard:** http://localhost:8501

---

## 📡 Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Health check básico |
| `GET` | `/health` | Estado de API y DB |
| `GET` | `/summary` | Métricas generales del dataset |
| `GET` | `/quotes` | Lista paginada con filtros |
| `GET` | `/quotes/{id}` | Quote por ID |
| `GET` | `/authors` | Estadísticas por autor |
| `GET` | `/tags` | Tags más frecuentes |
| `GET` | `/search?q=...` | Búsqueda full-text |

---

## 📁 Estructura

```
data-dashboard/
├── src/
│   ├── api.py           # FastAPI: endpoints REST + Pydantic models
│   └── dashboard.py     # Streamlit: UI interactiva + Plotly charts
├── tests/
│   └── test_api.py      # 12 tests con TestClient + DB temporal
├── .github/
│   └── workflows/
│       └── ci.yml       # Tests + deploy automático a Render
└── requirements.txt
```

---

## 🔧 Tecnologías

| Herramienta | Uso |
|-------------|-----|
| `FastAPI` | API REST con docs automáticas |
| `Pydantic` | Validación de datos y schemas |
| `Streamlit` | Dashboard interactivo sin JS |
| `Plotly` | Gráficas de barras, pie, scatter, treemap |
| `pytest + TestClient` | Tests de integración de API |
| `GitHub Actions` | CI/CD + deploy automático |
| `Render` | Hosting gratuito del backend |

---

## 🌐 Deploy en Render (gratis)

1. Crea cuenta en [render.com](https://render.com)
2. Nuevo servicio → **Web Service** → conecta tu repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn src.api:app --host 0.0.0.0 --port $PORT`
5. Copia el **Deploy Hook URL** y agrégalo en GitHub Secrets como `RENDER_DEPLOY_HOOK_URL`

A partir de ahí, cada push a `main` que pase los tests despliega automáticamente. ✅

---

## 🔗 Dependencia

Consume la base de datos SQLite generada por el [Web Scraper Pipeline](../proyecto1_scraper).

## 📄 Licencia

MIT
