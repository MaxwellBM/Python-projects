"""
pipeline.py — Limpieza y transformación de datos con pandas
"""

import pandas as pd
from scraper import Quote
import logging

logger = logging.getLogger(__name__)


class DataPipeline:
    """Transforma una lista de Quote en un DataFrame limpio y enriquecido."""

    def __init__(self, quotes: list[Quote]):
        self.raw = quotes
        self.df: pd.DataFrame = pd.DataFrame()

    def build(self) -> "DataPipeline":
        records = [
            {
                "text": q.text,
                "author": q.author,
                "tags": ", ".join(q.tags),
                "tag_count": len(q.tags),
                "word_count": len(q.text.split()),
                "author_url": q.author_url or "",
            }
            for q in self.raw
        ]
        self.df = pd.DataFrame(records)
        return self

    def clean(self) -> "DataPipeline":
        self.df.drop_duplicates(subset=["text"], inplace=True)
        self.df["text"] = self.df["text"].str.strip()
        self.df["author"] = self.df["author"].str.strip().str.title()
        self.df.reset_index(drop=True, inplace=True)
        logger.info(f"Dataset limpio: {len(self.df)} filas")
        return self

    def enrich(self) -> "DataPipeline":
        self.df["length_category"] = pd.cut(
            self.df["word_count"],
            bins=[0, 10, 20, 50, 9999],
            labels=["corta", "media", "larga", "muy_larga"],
        )
        self.df["has_love_tag"] = self.df["tags"].str.contains("love", case=False)
        return self

    def summary(self) -> dict:
        return {
            "total_quotes": len(self.df),
            "unique_authors": self.df["author"].nunique(),
            "avg_words": round(self.df["word_count"].mean(), 1),
            "top_author": self.df["author"].value_counts().idxmax(),
            "most_common_tag": (
                self.df["tags"]
                .str.split(", ")
                .explode()
                .value_counts()
                .idxmax()
            ),
        }

    def run(self) -> pd.DataFrame:
        return self.build().clean().enrich().df


if __name__ == "__main__":
    from scraper import QuoteScraper

    quotes = QuoteScraper().scrape(max_pages=2)
    pipeline = DataPipeline(quotes)
    df = pipeline.run()
    print(df.head())
    print("\nResumen:", pipeline.summary())
