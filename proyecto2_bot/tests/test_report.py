"""
tests/test_report.py — Tests para el generador de reportes
"""

import pytest
import sys
import sqlite3
import pandas as pd
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from report import ReportGenerator
from db import Storage


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_storage():
    storage = MagicMock(spec=Storage)
    storage.db_exists.return_value = True
    storage.total_quotes.return_value = 50
    storage.unique_authors.return_value = 23
    storage.avg_words.return_value = 18.4
    storage.top_authors.return_value = pd.DataFrame(
        {"author": ["Albert Einstein", "Mark Twain"], "quotes": [5, 3]}
    )
    storage.top_tags.return_value = pd.DataFrame(
        {"tag": ["inspirational", "life", "humor"], "count": [10, 8, 5]}
    )
    storage.search_author.return_value = pd.DataFrame(
        {"text": ["Imagination is more important than knowledge."], "author": ["Albert Einstein"], "tags": ["imagination"]}
    )
    return storage


@pytest.fixture
def generator(mock_storage):
    return ReportGenerator(mock_storage)


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_resumen_contains_total(generator):
    msg = generator.resumen()
    assert "50" in msg


def test_resumen_contains_author(generator):
    msg = generator.resumen()
    assert "Albert Einstein" in msg


def test_top_autores_contains_medal(generator):
    msg = generator.top_autores()
    assert "🥇" in msg


def test_top_autores_contains_author_name(generator):
    msg = generator.top_autores()
    assert "Albert Einstein" in msg


def test_top_tags_contains_tag(generator):
    msg = generator.top_tags()
    assert "inspirational" in msg


def test_buscar_autor_found(generator):
    msg = generator.buscar_autor("Einstein")
    assert "Imagination" in msg


def test_buscar_autor_not_found(mock_storage):
    mock_storage.search_author.return_value = pd.DataFrame()
    gen = ReportGenerator(mock_storage)
    msg = gen.buscar_autor("Unknown")
    assert "No se encontraron" in msg


def test_no_db_returns_warning(mock_storage):
    mock_storage.db_exists.return_value = False
    gen = ReportGenerator(mock_storage)
    assert "No hay datos" in gen.resumen()
    assert "No hay datos" in gen.top_autores()
    assert "No hay datos" in gen.top_tags()
