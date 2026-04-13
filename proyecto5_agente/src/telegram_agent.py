"""
telegram_agent.py — Interface de Telegram para el agente IA
El usuario escribe instrucciones en lenguaje natural y el agente las ejecuta
"""

import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from agent import AIAgent

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Un agente por usuario (manejo de contexto independiente)
_agents: dict[int, AIAgent] = {}


def get_agent(user_id: int) -> AIAgent:
    if user_id not in _agents:
        _agents[user_id] = AIAgent(api_key=ANTHROPIC_KEY)
    return _agents[user_id]


# ── Handlers ──────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🤖 *Agente IA activo*\n\n"
        "Puedo ayudarte con:\n"
        "• Consultar estadísticas del dataset\n"
        "• Ejecutar cálculos y análisis\n"
        "• Actualizar datos con el scraper\n"
        "• Responder preguntas en lenguaje natural\n\n"
        "Simplemente escríbeme lo que necesitas.\n\n"
        "_Ejemplos:_\n"
        "• `¿Cuántos autores hay en el dataset?`\n"
        "• `Calcula el promedio de 45, 67, 89 y 23`\n"
        "• `Actualiza los datos del scraper`\n"
        "• `/reset` para reiniciar la conversación",
        parse_mode="Markdown",
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id in _agents:
        del _agents[user_id]
    await update.message.reply_text("🔄 Conversación reiniciada.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_text = update.message.text

    # Indicador de "escribiendo..."
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing",
    )

    agent = get_agent(user_id)
    result = agent.run(user_text)

    # Construir respuesta con metadata
    response = result.answer
    if result.tools_used:
        tools_str = ", ".join(f"`{t}`" for t in result.tools_used)
        response += f"\n\n_Herramientas usadas: {tools_str} · {result.steps} pasos_"

    if not result.success:
        response = f"⚠️ {response}"

    # Telegram tiene límite de 4096 caracteres
    if len(response) > 4000:
        response = response[:4000] + "...\n_(respuesta truncada)_"

    await update.message.reply_text(response, parse_mode="Markdown")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Error: {context.error}")
    if isinstance(update, Update) and update.message:
        await update.message.reply_text(
            "❌ Ocurrió un error. Por favor intenta de nuevo."
        )


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN no encontrado en .env")
    if not ANTHROPIC_KEY:
        raise ValueError("ANTHROPIC_API_KEY no encontrado en .env")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info("Agente Telegram iniciado. Ctrl+C para detener.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
