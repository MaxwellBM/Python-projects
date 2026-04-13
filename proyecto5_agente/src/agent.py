"""
agent.py — Agente IA que razona, usa herramientas y ejecuta tareas automáticamente
"""

import logging
import json
from typing import Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class AgentMessage:
    role: str  # "user" | "assistant" | "tool"
    content: str
    tool_name: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class AgentResult:
    success: bool
    answer: str
    tools_used: list[str] = field(default_factory=list)
    steps: int = 0


class Tool:
    """Herramienta base que el agente puede invocar."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def run(self, input_text: str) -> str:
        raise NotImplementedError


class DataAPITool(Tool):
    """Consulta la API REST del pipeline de datos."""

    def __init__(self, api_url: str = "http://localhost:8000"):
        super().__init__(
            name="data_api",
            description="Consulta estadísticas del dataset: resumen, autores, tags, quotes.",
        )
        self.api_url = api_url

    def run(self, input_text: str) -> str:
        import requests
        endpoints = {
            "resumen": "/summary",
            "summary": "/summary",
            "autores": "/authors",
            "authors": "/authors",
            "tags": "/tags",
            "quotes": "/quotes?limit=5",
        }
        key = input_text.lower().strip()
        endpoint = next((v for k, v in endpoints.items() if k in key), "/summary")
        try:
            r = requests.get(f"{self.api_url}{endpoint}", timeout=5)
            r.raise_for_status()
            data = r.json()
            return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Error al consultar API: {e}"


class WebSearchTool(Tool):
    """Búsqueda web simulada (en producción conectar a SerpAPI o DuckDuckGo)."""

    def __init__(self):
        super().__init__(
            name="web_search",
            description="Busca información actualizada en internet sobre cualquier tema.",
        )

    def run(self, input_text: str) -> str:
        # En producción: usar requests a SerpAPI, DuckDuckGo API, etc.
        return (
            f"[Resultado simulado para: '{input_text}']\n"
            "Para conectar búsqueda real, configura SERPAPI_KEY en .env "
            "y reemplaza este método con una llamada a la API."
        )


class PythonREPLTool(Tool):
    """Ejecuta código Python de forma segura para cálculos y análisis."""

    def __init__(self):
        super().__init__(
            name="python_repl",
            description="Ejecuta código Python para cálculos, análisis de datos o transformaciones.",
        )
        self._allowed_imports = {"math", "statistics", "json", "datetime", "collections"}

    def run(self, code: str) -> str:
        # Validación básica de seguridad
        forbidden = ["import os", "import sys", "import subprocess", "open(", "__import__"]
        for term in forbidden:
            if term in code:
                return f"Error: código no permitido (contiene '{term}')"
        try:
            namespace: dict[str, Any] = {}
            exec(code, {"__builtins__": {"print": print, "len": len, "range": range,
                                          "sum": sum, "max": max, "min": min,
                                          "round": round, "sorted": sorted}},
                 namespace)
            result = namespace.get("result", "Código ejecutado sin valor de retorno")
            return str(result)
        except Exception as e:
            return f"Error de ejecución: {e}"


class ScraperTool(Tool):
    """Lanza el scraper del pipeline ETL para actualizar datos."""

    def __init__(self):
        super().__init__(
            name="scraper",
            description="Ejecuta el scraper para obtener datos frescos del pipeline ETL.",
        )

    def run(self, input_text: str) -> str:
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent))
            from scraper_mini import run_scraper
            count = run_scraper(max_pages=2)
            return f"Scraper completado: {count} registros actualizados."
        except ImportError:
            return "Scraper ejecutado (modo simulado). Conecta src/scraper.py del Proyecto 1."
        except Exception as e:
            return f"Error en scraper: {e}"


class AIAgent:
    """
    Agente de IA con ciclo ReAct (Reason → Act → Observe).
    Usa la API de Anthropic para razonar y decidir qué herramienta usar.
    """

    SYSTEM_PROMPT = """Eres un agente de automatización de datos inteligente.
Tienes acceso a las siguientes herramientas:
{tools}

Para responder, sigue este ciclo:
1. THOUGHT: Razona qué necesitas hacer
2. ACTION: Llama a una herramienta con formato JSON: {{"tool": "nombre", "input": "parámetro"}}
3. OBSERVATION: Analiza el resultado
4. ANSWER: Responde al usuario con la información obtenida

Si no necesitas herramientas, responde directamente con ANSWER: <tu respuesta>.
Siempre responde en español."""

    def __init__(self, api_key: str, tools: list[Tool] | None = None):
        self.api_key = api_key
        self.tools: dict[str, Tool] = {}
        self.history: list[AgentMessage] = []
        self.max_iterations = 5

        default_tools = tools or [DataAPITool(), WebSearchTool(), PythonREPLTool(), ScraperTool()]
        for t in default_tools:
            self.tools[t.name] = t

        logger.info(f"Agente iniciado con herramientas: {list(self.tools.keys())}")

    def _tools_description(self) -> str:
        return "\n".join(f"- {t.name}: {t.description}" for t in self.tools.values())

    def _call_claude(self, messages: list[dict]) -> str:
        import anthropic
        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=self.SYSTEM_PROMPT.format(tools=self._tools_description()),
            messages=messages,
        )
        return response.content[0].text

    def _parse_action(self, text: str) -> tuple[str, str] | None:
        """Extrae tool y input del texto de acción."""
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                action = json.loads(text[start:end])
                return action.get("tool"), action.get("input", "")
        except json.JSONDecodeError:
            pass
        return None

    def run(self, user_input: str) -> AgentResult:
        """Ciclo ReAct completo."""
        logger.info(f"Agente procesando: '{user_input}'")
        self.history.append(AgentMessage(role="user", content=user_input))

        messages = [{"role": "user", "content": user_input}]
        tools_used: list[str] = []

        for step in range(self.max_iterations):
            response_text = self._call_claude(messages)
            logger.info(f"Paso {step + 1}: {response_text[:120]}...")

            # ¿El agente quiere usar una herramienta?
            if "ACTION:" in response_text:
                action_part = response_text.split("ACTION:")[-1].strip()
                parsed = self._parse_action(action_part)

                if parsed:
                    tool_name, tool_input = parsed
                    if tool_name in self.tools:
                        logger.info(f"Ejecutando herramienta: {tool_name}({tool_input[:60]})")
                        observation = self.tools[tool_name].run(tool_input)
                        tools_used.append(tool_name)

                        messages.append({"role": "assistant", "content": response_text})
                        messages.append({
                            "role": "user",
                            "content": f"OBSERVATION: {observation}\n\nContinúa con el análisis."
                        })
                        continue
                    else:
                        messages.append({"role": "assistant", "content": response_text})
                        messages.append({
                            "role": "user",
                            "content": f"OBSERVATION: Herramienta '{tool_name}' no disponible."
                        })
                        continue

            # ¿El agente tiene una respuesta final?
            if "ANSWER:" in response_text:
                answer = response_text.split("ANSWER:")[-1].strip()
                self.history.append(AgentMessage(role="assistant", content=answer))
                return AgentResult(
                    success=True,
                    answer=answer,
                    tools_used=tools_used,
                    steps=step + 1,
                )

            # Respuesta directa sin ciclo ReAct
            self.history.append(AgentMessage(role="assistant", content=response_text))
            return AgentResult(
                success=True,
                answer=response_text,
                tools_used=tools_used,
                steps=step + 1,
            )

        return AgentResult(
            success=False,
            answer="Se alcanzó el límite de iteraciones sin respuesta definitiva.",
            tools_used=tools_used,
            steps=self.max_iterations,
        )

    def chat(self, user_input: str) -> str:
        """Interfaz simplificada: recibe texto, devuelve texto."""
        result = self.run(user_input)
        return result.answer
