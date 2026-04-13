"""
db.py — Capa de acceso a datos (reutiliza la DB del Proyecto 1)
"""

import sqlite3
import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "data" / "quotes.db"


class Storage:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def query(self, sql: str, params: tuple = ()) -> pd.DataFrame:
        try:
            with self._connect() as conn:
                return pd.read_sql(sql, conn, params=params)
        except Exception as e:
            logger.error(f"Error en query: {e}")
            return pd.DataFrame()

    def total_quotes(self) -> int:
        df = self.query("SELECT COUNT(*) as total FROM quotes")
        return int(df["total"].iloc[0]) if not df.empty else 0

    def unique_authors(self) -> int:
        df = self.query("SELECT COUNT(DISTINCT author) as total FROM quotes")
        return int(df["total"].iloc[0]) if not df.empty else 0

    def avg_words(self) -> float:
        df = self.query("SELECT AVG(word_count) as avg FROM quotes")
        return round(float(df["avg"].iloc[0]), 1) if not df.empty else 0.0

    def top_authors(self, limit: int = 5) -> pd.DataFrame:
        return self.query(
            "SELECT author, COUNT(*) as quotes FROM quotes GROUP BY author ORDER BY quotes DESC LIMIT ?",
            (limit,),
        )

    def top_tags(self, limit: int = 8) -> pd.DataFrame:
        df = self.query("SELECT tags FROM quotes WHERE tags != ''")
        if df.empty:
            return pd.DataFrame()
        tags_series = df["tags"].str.split(", ").explode().str.strip()
        return (
            tags_series.value_counts()
            .head(limit)
            .reset_index()
            .rename(columns={"index": "tag", "tags": "count", "count": "count"})
        )

    def search_author(self, name: str) -> pd.DataFrame:
        return self.query(
            "SELECT text, author, tags FROM quotes WHERE author LIKE ? LIMIT 5",
            (f"%{name}%",),
        )

    def db_exists(self) -> bool:
        return self.db_path.exists()
