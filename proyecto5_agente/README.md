# 🧠 Agente IA — Automatización con Lenguaje Natural

![CI](https://github.com/TU_USUARIO/ai-agent/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Claude](https://img.shields.io/badge/Claude-Sonnet-orange?logo=anthropic)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram)

Agente de IA que recibe instrucciones en lenguaje natural por Telegram, razona sobre qué herramientas usar, las ejecuta y responde con los resultados. Implementa el patrón **ReAct** (Reason + Act).

---

## 🧠 ¿Cómo funciona?

El agente usa el ciclo **ReAct**:

```
Usuario: "¿Cuántos autores hay y cuál es el promedio de palabras?"
    ↓
THOUGHT: Necesito consultar la API para obtener el resumen del dataset
    ↓
ACTION: {"tool": "data_api", "input": "resumen"}
    ↓
OBSERVATION: {"total_quotes": 50, "unique_authors": 23, "avg_word_count": 18.4}
    ↓
ANSWER: El dataset tiene 23 autores únicos con un promedio de 18.4 palabras por quote.
```

---

## 🛠️ Herramientas disponibles

| Herramienta | Descripción |
|-------------|-------------|
| `data_api` | Consulta la REST API del pipeline ETL |
| `python_repl` | Ejecuta código Python para cálculos |
| `web_search` | Busca información en internet |
| `scraper` | Lanza el scraper para actualizar datos |

Agregar una herramienta nueva es tan simple como heredar de `Tool` y registrarla.

---

## 🚀 Instalación

```bash
git clone https://github.com/TU_USUARIO/ai-agent
cd ai-agent
pip install -r requirements.txt
cp .env.example .env  # agrega ANTHROPIC_API_KEY y TELEGRAM_TOKEN
```

### Obtener API Key de Anthropic
1. Regístrate en [console.anthropic.com](https://console.anthropic.com)
2. Ve a **API Keys** → **Create Key**
3. Copia y pega en tu `.env`

---

## ▶️ Uso

```bash
# Modo CLI (para probar sin Telegram)
python src/cli.py

# Modo Telegram
python src/telegram_agent.py
```

### Ejemplos de consultas

```
¿Cuántos autores hay en el dataset?
Dame un resumen de las estadísticas
Calcula el área de un círculo de radio 5
¿Cuál es el autor más citado?
Actualiza los datos del scraper
Busca información sobre automatización RPA
```

---

## 📁 Estructura

```
ai-agent/
├── src/
│   ├── agent.py            # Clase AIAgent con ciclo ReAct + herramientas
│   ├── telegram_agent.py   # Interface de Telegram (un agente por usuario)
│   └── cli.py              # Interface de línea de comandos
├── tests/
│   └── test_agent.py       # 12 tests con mocks de Anthropic
├── .env.example
├── .github/
│   └── workflows/
│       └── ci.yml
└── requirements.txt
```

---

## 🔧 Agregar una herramienta nueva

```python
from agent import Tool

class MiHerramienta(Tool):
    def __init__(self):
        super().__init__(
            name="mi_herramienta",
            description="Describe qué hace para que el agente sepa cuándo usarla.",
        )

    def run(self, input_text: str) -> str:
        # Tu lógica aquí
        return "resultado"

# Registrar en el agente
agent = AIAgent(api_key=key, tools=[..., MiHerramienta()])
```

---

## 🔗 Integración con el ecosistema

Este agente une todos los proyectos anteriores:

- Consulta la **DB del Proyecto 1** (via data_api)
- Comparte la interfaz de **Telegram del Proyecto 2**
- Puede lanzar la **automatización RPA del Proyecto 3**
- Consume la **API REST del Proyecto 4**

---

## 🔧 Tecnologías

| Herramienta | Uso |
|-------------|-----|
| `anthropic` | SDK oficial de Claude |
| `python-telegram-bot` | Interface de usuario |
| Patrón ReAct | Razonamiento + acción iterativo |
| `dataclasses` | Modelos tipados |
| `unittest.mock` | Tests sin API real |

## 📄 Licencia

MIT
