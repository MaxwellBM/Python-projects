"""
api.py — API REST con FastAPI que expone los datos del pipeline ETL
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "data" / "quotes.db"

app = FastAPI(
    title="Data Pipeline API",
    description="API REST para consultar datos del scraper ETL",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Modelos ───────────────────────────────────────────────────────────────────

class Quote(BaseModel):
    text: str
    author: str
    tags: str
    word_count: int
    length_category: Optional[str] = None


class Summary(BaseModel):
    total_quotes: int
    unique_authors: int
    avg_word_count: float
    top_author: str
    generated_at: str


class AuthorStats(BaseModel):
    author: str
    quote_count: int
    avg_words: float


# ── Utilidades ────────────────────────────────────────────────────────────────

def get_db() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail="Base de datos no disponible. Ejecuta el pipeline primero.",
        )
    return sqlite3.connect(DB_PATH)


def query_df(sql: str, params: tuple = ()) -> pd.DataFrame:
    with get_db() as conn:
        return pd.read_sql(sql, conn, params=params)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Data Pipeline API v1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    db_ok = DB_PATH.exists()
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "not found",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/summary", response_model=Summary, tags=["Stats"])
def get_summary():
    df = query_df("SELECT * FROM quotes")
    top = df["author"].value_counts().idxmax() if not df.empty else "N/A"
    return Summary(
        total_quotes=len(df),
        unique_authors=df["author"].nunique(),
        avg_word_count=round(df["word_count"].mean(), 1),
        top_author=top,
        generated_at=datetime.utcnow().isoformat(),
    )


@app.get("/quotes", response_model=list[Quote], tags=["Quotes"])
def get_quotes(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    author: Optional[str] = Query(default=None, description="Filtrar por autor"),
):
    sql = "SELECT text, author, tags, word_count, length_category FROM quotes"
    params: list = []
    if author:
        sql += " WHERE author LIKE ?"
        params.append(f"%{author}%")
    sql += " LIMIT ? OFFSET ?"
    params += [limit, offset]
    df = query_df(sql, tuple(params))
    return df.to_dict(orient="records")


@app.get("/quotes/{quote_id}", response_model=Quote, tags=["Quotes"])
def get_quote(quote_id: int):
    df = query_df(
        "SELECT text, author, tags, word_count, length_category FROM quotes LIMIT 1 OFFSET ?",
        (quote_id,),
    )
    if df.empty:
        raise HTTPException(status_code=404, detail="Quote no encontrada")
    return df.iloc[0].to_dict()


@app.get("/authors", response_model=list[AuthorStats], tags=["Authors"])
def get_authors(limit: int = Query(default=10, ge=1, le=50)):
    df = query_df(
        """SELECT author,
                  COUNT(*) as quote_count,
                  ROUND(AVG(word_count), 1) as avg_words
           FROM quotes
           GROUP BY author
           ORDER BY quote_count DESC
           LIMIT ?""",
        (limit,),
    )
    return df.to_dict(orient="records")


@app.get("/tags", tags=["Stats"])
def get_tags(limit: int = Query(default=10, ge=1, le=50)):
    df = query_df("SELECT tags FROM quotes WHERE tags != ''")
    if df.empty:
        return []
    counts = (
        df["tags"].str.split(", ").explode().str.strip().value_counts().head(limit)
    )
    return [{"tag": tag, "count": int(cnt)} for tag, cnt in counts.items()]


@app.get("/search", response_model=list[Quote], tags=["Quotes"])
def search(
    q: str = Query(..., min_length=2, description="Texto a buscar en quotes o autor"),
    limit: int = Query(default=5, ge=1, le=20),
):
    df = query_df(
        """SELECT text, author, tags, word_count, length_category
           FROM quotes
           WHERE text LIKE ? OR author LIKE ?
           LIMIT ?""",
        (f"%{q}%", f"%{q}%", limit),
    )
    return df.to_dict(orient="records")
