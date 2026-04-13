# 🤖 RPA con Selenium — Automatización Web

![CI](https://github.com/TU_USUARIO/rpa-selenium/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Selenium](https://img.shields.io/badge/Selenium-4.21-43B02A?logo=selenium)

Bot RPA que automatiza tareas repetitivas en sitios web: login, extracción de tablas, manejo de alerts y generación de reportes Excel. Ejecutado automáticamente cada día laboral con GitHub Actions.

---

## ✨ Tareas automatizadas

| Tarea | Descripción | Output |
|-------|-------------|--------|
| Login | Autenticación en formulario | Screenshot de evidencia |
| Extracción de tabla | Scraping de tabla HTML dinámica | DataFrame + Excel |
| Manejo de alerts | JS Alert, Confirm y Prompt | Resultados en JSON |
| Reporte automático | Extrae contenido dinámico | `.txt` + `.xlsx` |

---

## 🚀 Instalación

```bash
git clone https://github.com/TU_USUARIO/rpa-selenium
cd rpa-selenium
pip install -r requirements.txt

# Chrome debe estar instalado en el sistema
# ChromeDriver se gestiona automáticamente con Selenium 4+
```

## ▶️ Uso

```bash
# Ejecutar automatización completa
python src/main.py

# Solo módulo RPA
python src/rpa.py

# Correr tests
pytest tests/ -v --cov=src
```

## 📁 Estructura

```
rpa-selenium/
├── src/
│   ├── rpa.py               # Bot RPA con Selenium (context manager)
│   ├── excel_processor.py   # Generador de reportes Excel formateados
│   └── main.py              # Orquestador del flujo completo
├── tests/
│   └── test_rpa.py          # Tests con mocks de Selenium y pytest
├── screenshots/             # Evidencia de ejecución (auto-generado)
├── data/                    # Outputs: Excel, JSON, TXT (auto-generado)
├── .github/
│   └── workflows/
│       └── ci.yml           # CI/CD + ejecución automática L-V
└── requirements.txt
```

---

## 🧠 Patrones de diseño utilizados

- **Context Manager** (`__enter__`/`__exit__`) para gestión segura del WebDriver
- **WebDriverWait + Expected Conditions** para esperas explícitas robustas
- **Dataclasses** para modelar datos extraídos (`TableRow`, `LoginResult`)
- **Separación de responsabilidades**: `rpa.py` extrae, `excel_processor.py` reporta
- **Mocks** en tests para no depender de Chrome en CI

---

## 📊 Output de ejemplo

```
10:00:01 [INFO] ── Tarea 1: Login ──
10:00:03 [INFO] Screenshot guardado: screenshots/login_success_1234.png
10:00:03 [INFO] ── Tarea 2: Extracción de tabla ──
10:00:04 [INFO] Extraídas 4 filas de la tabla
10:00:04 [INFO] ── Tarea 3: Manejo de alerts ──
10:00:06 [INFO] Alerts manejados: {'alert_text': 'I am a JS Alert', ...}
10:00:06 [INFO] ── Tarea 4: Descarga de reporte ──

📋 RESUMEN DE EJECUCIÓN
----------------------------------------
  Login:            ✅ Login exitoso
  Filas extraídas:  4
  Alerts manejados: 4
  Excel generado:   ✅ data/rpa_report.xlsx
  Screenshots:      📸 screenshots/
----------------------------------------
Automatización completada ✅
```

## 🔧 Tecnologías

| Herramienta | Uso |
|-------------|-----|
| `Selenium 4` | Automatización del navegador |
| `openpyxl` | Generación de Excel formateado |
| `dataclasses` | Modelos de datos tipados |
| `pytest + mock` | Tests sin dependencia de Chrome |
| `GitHub Actions` | CI/CD + ejecución diaria |

## 📄 Licencia

MIT
