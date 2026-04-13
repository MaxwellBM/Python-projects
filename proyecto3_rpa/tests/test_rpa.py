"""
tests/test_rpa.py — Tests del bot RPA usando mocks de Selenium
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rpa import RPABot, LoginResult, TableRow
from excel_processor import ExcelReporter


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_driver():
    driver = MagicMock()
    driver.title = "Test Page"
    return driver


@pytest.fixture
def bot(mock_driver):
    b = RPABot(headless=True)
    b.driver = mock_driver
    b.wait = MagicMock()
    return b


@pytest.fixture
def sample_rows():
    return [
        TableRow("Smith", "John", "jsmith@example.com", "$50.00", "http://example.com", "edit delete"),
        TableRow("Doe", "Jane", "jane@example.com", "$25.00", "http://doe.com", "edit delete"),
    ]


# ── Tests LoginResult ─────────────────────────────────────────────────────────

def test_login_result_success():
    result = LoginResult(success=True, message="Login exitoso", username="admin")
    assert result.success is True
    assert result.username == "admin"


def test_login_result_failure():
    result = LoginResult(success=False, message="Credenciales incorrectas")
    assert result.success is False


# ── Tests TableRow ────────────────────────────────────────────────────────────

def test_table_row_creation(sample_rows):
    row = sample_rows[0]
    assert row.last_name == "Smith"
    assert row.email == "jsmith@example.com"


def test_table_row_fields():
    row = TableRow("García", "Ana", "ana@test.com", "$100.00", "http://ana.com", "edit")
    assert row.first_name == "Ana"
    assert row.due == "$100.00"


# ── Tests RPABot context manager ──────────────────────────────────────────────

def test_rpa_bot_context_manager():
    with patch("rpa.webdriver.Chrome") as mock_chrome:
        mock_chrome.return_value = MagicMock()
        with RPABot(headless=True) as bot:
            assert bot.driver is not None
        mock_chrome.return_value.quit.assert_called_once()


def test_screenshot_creates_file(bot, tmp_path):
    bot.driver.save_screenshot = MagicMock(return_value=True)
    with patch("rpa.SCREENSHOTS_DIR", tmp_path):
        path = bot.screenshot("test")
    assert path.suffix == ".png"


# ── Tests ExcelReporter ───────────────────────────────────────────────────────

def test_excel_reporter_generates_file(sample_rows, tmp_path):
    output = tmp_path / "test_report.xlsx"
    reporter = ExcelReporter(output_path=output)
    rpa_results = {
        "login": {"success": True, "message": "Login exitoso"},
        "table": {"rows_extracted": 2},
        "alerts": {"alert_text": "I am a JS Alert"},
        "report": {"saved": True},
    }
    result_path = reporter.generate(sample_rows, rpa_results)
    assert result_path.exists()
    assert result_path.suffix == ".xlsx"


def test_excel_reporter_empty_rows(tmp_path):
    output = tmp_path / "empty_report.xlsx"
    reporter = ExcelReporter(output_path=output)
    result_path = reporter.generate([], {"login": {"success": False, "message": "Error"}})
    assert result_path.exists()
