"""
main.py — Orquesta el flujo completo de automatización RPA
"""

import json
import logging
from pathlib import Path

from rpa import RPABot
from excel_processor import ExcelReporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def run():
    logger.info("=" * 55)
    logger.info("  Iniciando automatización RPA con Selenium")
    logger.info("=" * 55)

    # 1. Ejecutar todas las tareas RPA
    with RPABot(headless=True) as bot:
        results = bot.run_full_pipeline()
        table_rows = bot.extract_table()

    # 2. Generar reporte Excel
    logger.info("── Generando reporte Excel ──")
    reporter = ExcelReporter()
    excel_path = reporter.generate(table_rows, results)

    # 3. Guardar resultados JSON
    json_path = Path("data/results.json")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # 4. Reporte en consola
    logger.info("\n📋 RESUMEN DE EJECUCIÓN")
    logger.info("-" * 40)
    logger.info(f"  Login:            {'✅' if results['login']['success'] else '❌'} {results['login']['message']}")
    logger.info(f"  Filas extraídas:  {results['table']['rows_extracted']}")
    logger.info(f"  Alerts manejados: {len(results['alerts'])}")
    logger.info(f"  Reporte txt:      {'✅' if results['report']['saved'] else '❌'}")
    logger.info(f"  Excel generado:   ✅ {excel_path}")
    logger.info(f"  JSON guardado:    ✅ {json_path}")
    logger.info(f"  Screenshots:      📸 screenshots/")
    logger.info("-" * 40)
    logger.info("Automatización completada ✅")


if __name__ == "__main__":
    run()
