"""
tests/test_agent.py — Tests del agente IA con mocks de Anthropic
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent import AIAgent, AgentResult, AgentMessage, Tool, PythonREPLTool, DataAPITool


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_claude_response():
    """Mock de respuesta directa de Claude sin herramientas."""
    mock = MagicMock()
    mock.content = [MagicMock(text="ANSWER: El dataset tiene 50 quotes de 23 autores.")]
    return mock


@pytest.fixture
def mock_claude_with_tool():
    """Mock de Claude que primero llama herramienta y luego responde."""
    call_count = {"n": 0}

    def side_effect(*args, **kwargs):
        call_count["n"] += 1
        mock = MagicMock()
        if call_count["n"] == 1:
            mock.content = [MagicMock(
                text='THOUGHT: Debo consultar la API.\nACTION: {"tool": "python_repl", "input": "result = 2 + 2"}'
            )]
        else:
            mock.content = [MagicMock(text="ANSWER: El resultado es 4.")]
        return mock

    return side_effect


@pytest.fixture
def agent():
    return AIAgent(api_key="fake-key-for-tests")


# ── Tests Tool base ───────────────────────────────────────────────────────────

def test_tool_creation():
    tool = PythonREPLTool()
    assert tool.name == "python_repl"
    assert len(tool.description) > 0


def test_python_repl_basic():
    tool = PythonREPLTool()
    result = tool.run("result = 2 + 2")
    assert "4" in result


def test_python_repl_math():
    tool = PythonREPLTool()
    result = tool.run("result = round(3.14159 * 7 ** 2, 2)")
    assert "153" in result


def test_python_repl_blocks_os():
    tool = PythonREPLTool()
    result = tool.run("import os; result = os.listdir('.')")
    assert "Error" in result


def test_python_repl_blocks_subprocess():
    tool = PythonREPLTool()
    result = tool.run("import subprocess; result = subprocess.run(['ls'])")
    assert "Error" in result


# ── Tests AIAgent ─────────────────────────────────────────────────────────────

def test_agent_initialization(agent):
    assert "python_repl" in agent.tools
    assert "data_api" in agent.tools
    assert "web_search" in agent.tools
    assert "scraper" in agent.tools


def test_agent_direct_answer(agent, mock_claude_response):
    with patch("anthropic.Anthropic") as MockAnthropic:
        MockAnthropic.return_value.messages.create.return_value = mock_claude_response
        agent.api_key = "fake"
        result = agent.run("¿Cuántos quotes hay?")

    assert isinstance(result, AgentResult)


def test_agent_result_structure():
    result = AgentResult(success=True, answer="Hola", tools_used=["python_repl"], steps=2)
    assert result.success is True
    assert result.steps == 2
    assert "python_repl" in result.tools_used


def test_agent_message_structure():
    msg = AgentMessage(role="user", content="test")
    assert msg.role == "user"
    assert msg.timestamp is not None


def test_agent_parse_action_valid(agent):
    text = 'ACTION: {"tool": "python_repl", "input": "result = 1 + 1"}'
    result = agent._parse_action(text)
    assert result is not None
    assert result[0] == "python_repl"


def test_agent_parse_action_invalid(agent):
    result = agent._parse_action("sin formato json aquí")
    assert result is None


def test_agent_history_records(agent, mock_claude_response):
    with patch("anthropic.Anthropic") as MockAnthropic:
        MockAnthropic.return_value.messages.create.return_value = mock_claude_response
        agent.run("Hola")
    assert len(agent.history) >= 1
    assert agent.history[0].role == "user"


def test_agent_tools_description(agent):
    desc = agent._tools_description()
    assert "python_repl" in desc
    assert "data_api" in desc
