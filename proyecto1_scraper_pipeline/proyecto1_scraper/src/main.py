"""
main.py — Orquesta el pipeline completo: scrape → transform → store → report
"""

import logging
from pathlib import Path

from scraper import QuoteScraper
from pipeline import DataPipeline
from storage import Storage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_pipeline(max_pages: int = 5) -> None:
    logger.info("=" * 50)
    logger.info("Iniciando pipeline de datos")
    logger.info("=" * 50)

    # 1. Scraping
    logger.info("[1/3] Extrayendo datos...")
    scraper = QuoteScraper()
    quotes = scraper.scrape(max_pages=max_pages)

    if not quotes:
        logger.error("No se obtuvieron datos. Abortando.")
        return

    # 2. Transformación
    logger.info("[2/3] Transformando datos...")
    pipeline = DataPipeline(quotes)
    df = pipeline.run()
    summary = pipeline.summary()

    # 3. Almacenamiento
    logger.info("[3/3] Guardando datos...")
    storage = Storage()
    storage.save(df)
    storage.export_csv(Path("data/quotes_export.csv"))

    # Reporte final
    logger.info("\n📊 REPORTE FINAL")
    logger.info("-" * 30)
    for key, value in summary.items():
        logger.info(f"  {key:<20}: {value}")
    logger.info("-" * 30)
    logger.info("Pipeline completado exitosamente ✅")


if __name__ == "__main__":
    run_pipeline(max_pages=5)
