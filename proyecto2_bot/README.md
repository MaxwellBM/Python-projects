# 🤖 Bot de Telegram — Reportes Automáticos

![CI](https://github.com/TU_USUARIO/telegram-data-bot/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram)

Bot de Telegram que consulta datos del pipeline ETL y envía reportes automáticos diarios. Construido con `python-telegram-bot` y `APScheduler`.

---

## 🚀 Setup en 3 pasos

### 1. Crear el bot en Telegram
1. Abre [@BotFather](https://t.me/botfather) en Telegram
2. Envía `/newbot` y sigue las instrucciones
3. Copia el **token** que te da

### 2. Obtener tu Chat ID
1. Envía un mensaje a tu bot
2. Visita: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Copia el valor de `"id"` dentro de `"chat"`

### 3. Configurar y correr
```bash
git clone https://github.com/TU_USUARIO/telegram-data-bot
cd telegram-data-bot
pip install -r requirements.txt
cp .env.example .env        # edita con tu TOKEN y CHAT_ID
python src/bot.py
```

---

##  Comandos disponibles

| Comando | Descripción |
|---------|-------------|
| `/start` | Menú principal con botones |
| `/reporte` | Resumen completo del dataset |
| `/top_autores` | Top 5 autores con más quotes |
| `/top_tags` | Tags más frecuentes con barra visual |
| `/buscar Einstein` | Busca quotes de un autor específico |
| `/alerta` | Activa reporte diario automático a las 8am |

---

##  Estructura

```
telegram-data-bot/
├── src/
│   ├── bot.py       # Handlers + scheduler
│   ├── db.py        # Capa de acceso a SQLite
│   └── report.py    # Generador de mensajes Markdown
├── tests/
│   └── test_report.py  # 8 tests con mocks
├── .env.example
├── .github/
│   └── workflows/
│       └── ci.yml
└── requirements.txt
```

---

##  Tecnologías

| Herramienta | Uso |
|-------------|-----|
| `python-telegram-bot` | Framework del bot |
| `APScheduler` | Reportes programados |
| `pandas` + `SQLite` | Consulta de datos |
| `unittest.mock` | Tests sin DB real |
| `GitHub Actions` | CI automático |

---

##  Dependencia

Este bot consume la base de datos generada por el [Web Scraper Pipeline](../proyecto1_scraper). Ejecuta ese pipeline primero para tener datos.

##  Licencia  Maxwell Baxter

MIT
