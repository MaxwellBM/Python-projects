"""
storage.py — Guarda y consulta datos en SQLite y exporta a CSV
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
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, df: pd.DataFrame, table: str = "quotes") -> int:
        with sqlite3.connect(self.db_path) as conn:
            df.to_sql(table, conn, if_exists="replace", index=False)
        logger.info(f"Guardadas {len(df)} filas en tabla '{table}'")
        return len(df)

    def load(self, table: str = "quotes") -> pd.DataFrame:
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql(f"SELECT * FROM {table}", conn)

    def query(self, sql: str) -> pd.DataFrame:
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql(sql, conn)

    def export_csv(self, output_path: Path) -> None:
        df = self.load()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False, encoding="utf-8")
        logger.info(f"CSV exportado: {output_path}")


if __name__ == "__main__":
    from scraper import QuoteScraper
    from pipeline import DataPipeline

    quotes = QuoteScraper().scrape(max_pages=2)
    df = DataPipeline(quotes).run()

    storage = Storage()
    storage.save(df)

    result = storage.query(
        "SELECT author, COUNT(*) as total FROM quotes GROUP BY author ORDER BY total DESC LIMIT 5"
    )
    print("\nTop autores:\n", result.to_string(index=False))

    storage.export_csv(Path("data/quotes_export.csv"))
