# 🕷️ Web Scraper + Data Pipeline

![CI](https://github.com/TU_USUARIO/web-scraper-pipeline/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![pandas](https://img.shields.io/badge/pandas-2.2-150458?logo=pandas)
![License](https://img.shields.io/badge/license-MIT-green)

Pipeline ETL completo que extrae, transforma y almacena datos de la web de forma automatizada. Incluye CI/CD con GitHub Actions que ejecuta el scraper diariamente.

---

## 🏗️ Arquitectura

```
Web → scraper.py → pipeline.py → storage.py → SQLite / CSV
                                     ↑
                              GitHub Actions (daily)
```

## ✨ Features

- **Scraping robusto** con manejo de errores, reintentos y rate limiting
- **Pipeline ETL** con pandas: limpieza, transformación y enriquecimiento
- **Almacenamiento dual**: SQLite para consultas + CSV para exportación
- **CI/CD automático**: tests + lint + ejecución diaria con GitHub Actions
- **OOP**: clases `QuoteScraper`, `DataPipeline`, `Storage` desacopladas

## 🚀 Instalación

```bash
git clone https://github.com/TU_USUARIO/web-scraper-pipeline
cd web-scraper-pipeline
pip install -r requirements.txt
```

## ▶️ Uso

```bash
# Ejecutar pipeline completo
python src/main.py

# Solo scraping
python src/scraper.py

# Correr tests
pytest tests/ -v --cov=src
```

## 📁 Estructura

```
web-scraper-pipeline/
├── src/
│   ├── scraper.py       # Extracción con BeautifulSoup
│   ├── pipeline.py      # Transformación con pandas
│   ├── storage.py       # SQLite + CSV
│   └── main.py          # Orquestador
├── tests/
│   └── test_pipeline.py # 8 tests unitarios
├── data/                # Generado automáticamente
│   ├── quotes.db
│   └── quotes_export.csv
├── .github/
│   └── workflows/
│       └── ci.yml       # CI/CD pipeline
└── requirements.txt
```

## 🔧 Tecnologías

| Herramienta | Uso |
|-------------|-----|
| `requests` + `BeautifulSoup` | Scraping HTTP |
| `pandas` | ETL y análisis |
| `SQLite` | Persistencia |
| `pytest` | Testing |
| `GitHub Actions` | CI/CD |

## 📊 Output de ejemplo

```
10:00:01 [INFO] Iniciando pipeline de datos
10:00:02 [INFO] [1/3] Extrayendo datos...
10:00:05 [INFO] Total: 50 quotes extraídas
10:00:05 [INFO] [2/3] Transformando datos...
10:00:05 [INFO] Dataset limpio: 50 filas
10:00:05 [INFO] [3/3] Guardando datos...

📊 REPORTE FINAL
------------------------------
  total_quotes        : 50
  unique_authors      : 23
  avg_words           : 18.4
  top_author          : Albert Einstein
  most_common_tag     : inspirational
------------------------------
Pipeline completado exitosamente ✅
```

## 🤝 Contribuciones

PRs bienvenidos. Para cambios grandes, abre un issue primero.

## 📄 Licencia

MIT
