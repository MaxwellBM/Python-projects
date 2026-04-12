"""
tests/test_pipeline.py — Tests unitarios para pipeline y scraper
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scraper import Quote
from pipeline import DataPipeline


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_quotes():
    return [
        Quote(text="The world is a book", author="Saint Augustine", tags=["world", "books"]),
        Quote(text="Life is what happens", author="John Lennon", tags=["life"]),
        Quote(text="The world is a book", author="Saint Augustine", tags=["world", "books"]),  # duplicado
        Quote(text="In the middle of difficulty lies opportunity", author="Albert Einstein", tags=["inspiration"]),
    ]


@pytest.fixture
def pipeline(sample_quotes):
    return DataPipeline(sample_quotes)


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_build_creates_dataframe(pipeline):
    pipeline.build()
    assert isinstance(pipeline.df, pd.DataFrame)
    assert len(pipeline.df) > 0


def test_clean_removes_duplicates(pipeline):
    pipeline.build().clean()
    assert pipeline.df["text"].duplicated().sum() == 0


def test_clean_correct_count(pipeline):
    pipeline.build().clean()
    assert len(pipeline.df) == 3  # 4 - 1 duplicado


def test_enrich_adds_columns(pipeline):
    pipeline.build().clean().enrich()
    assert "length_category" in pipeline.df.columns
    assert "has_love_tag" in pipeline.df.columns


def test_word_count_positive(pipeline):
    pipeline.build()
    assert (pipeline.df["word_count"] > 0).all()


def test_summary_keys(pipeline):
    pipeline.build().clean().enrich()
    summary = pipeline.summary()
    expected_keys = {"total_quotes", "unique_authors", "avg_words", "top_author", "most_common_tag"}
    assert expected_keys.issubset(summary.keys())


def test_run_returns_dataframe(pipeline):
    df = pipeline.run()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_tags_joined_correctly(pipeline):
    pipeline.build()
    first_row = pipeline.df.iloc[0]
    assert isinstance(first_row["tags"], str)
