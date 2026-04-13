"""
bot.py — Bot de Telegram con comandos y reportes automáticos
"""

import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db import Storage
from report import ReportGenerator

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ── Comandos ──────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("📊 Reporte", callback_data="reporte")],
        [InlineKeyboardButton("👤 Top autores", callback_data="top_autores")],
        [InlineKeyboardButton("🏷️ Top tags", callback_data="top_tags")],
        [InlineKeyboardButton("🔍 Buscar autor", callback_data="buscar")],
    ]
    await update.message.reply_text(
        "👋 *Bot de Datos activo*\n\nElige una opción:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def reporte(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    storage = Storage()
    gen = ReportGenerator(storage)
    msg = gen.resumen()
    await update.message.reply_text(msg, parse_mode="Markdown")


async def top_autores(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    storage = Storage()
    gen = ReportGenerator(storage)
    msg = gen.top_autores()
    await update.message.reply_text(msg, parse_mode="Markdown")


async def top_tags(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    storage = Storage()
    gen = ReportGenerator(storage)
    msg = gen.top_tags()
    await update.message.reply_text(msg, parse_mode="Markdown")


async def buscar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Uso: `/buscar Einstein`", parse_mode="Markdown")
        return
    autor = " ".join(context.args)
    storage = Storage()
    gen = ReportGenerator(storage)
    msg = gen.buscar_autor(autor)
    await update.message.reply_text(msg, parse_mode="Markdown")


async def alerta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "✅ *Alerta activada*\nRecibirás el reporte diario a las *8:00 AM UTC*.",
        parse_mode="Markdown",
    )


# ── Callbacks de botones ──────────────────────────────────────────────────────

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    storage = Storage()
    gen = ReportGenerator(storage)

    handlers = {
        "reporte": gen.resumen,
        "top_autores": gen.top_autores,
        "top_tags": gen.top_tags,
        "buscar": lambda: "Usa el comando: `/buscar NombreAutor`",
    }
    msg = handlers.get(query.data, lambda: "Opción no reconocida")()
    await query.edit_message_text(msg, parse_mode="Markdown")


# ── Scheduler: reporte diario automático ─────────────────────────────────────

async def enviar_reporte_diario(app: Application) -> None:
    if not CHAT_ID:
        logger.warning("TELEGRAM_CHAT_ID no configurado, saltando reporte diario")
        return
    storage = Storage()
    gen = ReportGenerator(storage)
    msg = f"🌅 *Reporte Diario Automático*\n\n{gen.resumen()}"
    await app.bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
    logger.info("Reporte diario enviado")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN no encontrado en .env")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reporte", reporte))
    app.add_handler(CommandHandler("top_autores", top_autores))
    app.add_handler(CommandHandler("top_tags", top_tags))
    app.add_handler(CommandHandler("buscar", buscar))
    app.add_handler(CommandHandler("alerta", alerta))
    app.add_handler(CallbackQueryHandler(button_handler))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        enviar_reporte_diario,
        "cron",
        hour=8,
        minute=0,
        args=[app],
    )
    scheduler.start()

    logger.info("Bot iniciado. Presiona Ctrl+C para detener.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
