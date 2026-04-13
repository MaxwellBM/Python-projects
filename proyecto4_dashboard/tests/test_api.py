"""
tests/test_api.py — Tests de la API con FastAPI TestClient y DB temporal
"""

import pytest
import sqlite3
import sys
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def temp_db(tmp_path):
    """Crea una base de datos SQLite temporal con datos de prueba."""
    db_path = tmp_path / "quotes.db"
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE quotes (
            text TEXT, author TEXT, tags TEXT,
            word_count INTEGER, length_category TEXT, has_love_tag INTEGER
        )
    """)
    conn.executemany(
        "INSERT INTO quotes VALUES (?, ?, ?, ?, ?, ?)",
        [
            ("The world is a book.", "Saint Augustine", "world, books", 6, "corta", 0),
            ("Imagination is more important than knowledge.", "Albert Einstein", "imagination, knowledge", 7, "corta", 0),
            ("Life is what happens while you are busy.", "John Lennon", "life, love", 8, "corta", 1),
            ("In the middle of difficulty lies opportunity.", "Albert Einstein", "inspiration", 8, "corta", 0),
        ],
    )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def client(temp_db):
    from api import app, DB_PATH
    with patch("api.DB_PATH", temp_db):
        with TestClient(app) as c:
            yield c


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_health_with_db(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_summary_returns_correct_totals(client):
    r = client.get("/summary")
    assert r.status_code == 200
    data = r.json()
    assert data["total_quotes"] == 4
    assert data["unique_authors"] == 3


def test_get_quotes_default(client):
    r = client.get("/quotes")
    assert r.status_code == 200
    assert len(r.json()) == 4


def test_get_quotes_limit(client):
    r = client.get("/quotes?limit=2")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_get_quotes_filter_author(client):
    r = client.get("/quotes?author=Einstein")
    assert r.status_code == 200
    results = r.json()
    assert all("Einstein" in q["author"] for q in results)


def test_get_quote_by_id(client):
    r = client.get("/quotes/0")
    assert r.status_code == 200
    assert "text" in r.json()


def test_get_quote_not_found(client):
    r = client.get("/quotes/9999")
    assert r.status_code == 404


def test_get_authors(client):
    r = client.get("/authors")
    assert r.status_code == 200
    authors = r.json()
    assert len(authors) > 0
    assert "author" in authors[0]
    assert "quote_count" in authors[0]


def test_get_tags(client):
    r = client.get("/tags")
    assert r.status_code == 200
    tags = r.json()
    assert isinstance(tags, list)


def test_search(client):
    r = client.get("/search?q=Einstein")
    assert r.status_code == 200
    assert len(r.json()) > 0


def test_search_min_length(client):
    r = client.get("/search?q=a")
    assert r.status_code == 422
