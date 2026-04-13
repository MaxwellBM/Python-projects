"""
cli.py — Interfaz de línea de comandos para probar el agente localmente
"""

import os
import sys
from dotenv import load_dotenv
from agent import AIAgent

load_dotenv()

BANNER = """
╔══════════════════════════════════════════╗
║        🤖 Agente IA — CLI Mode           ║
║  Escribe tu consulta en lenguaje natural ║
║  'salir' o Ctrl+C para terminar          ║
╚══════════════════════════════════════════╝
"""

EXAMPLES = [
    "¿Cuántos autores hay en el dataset?",
    "Dame un resumen de las estadísticas",
    "Calcula el área de un círculo de radio 7",
    "Busca información sobre Python web scraping",
    "Actualiza los datos del scraper",
]


def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY no encontrada en .env")
        sys.exit(1)

    print(BANNER)
    print("Ejemplos de consultas:")
    for ex in EXAMPLES:
        print(f"  • {ex}")
    print()

    agent = AIAgent(api_key=api_key)

    while True:
        try:
            user_input = input("Tú: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nHasta luego 👋")
            break

        if not user_input:
            continue
        if user_input.lower() in ("salir", "exit", "quit"):
            print("Hasta luego 👋")
            break
        if user_input.lower() == "reset":
            agent = AIAgent(api_key=api_key)
            print("🔄 Conversación reiniciada\n")
            continue
        if user_input.lower() == "historia":
            for msg in agent.history:
                print(f"[{msg.role}] {msg.content[:80]}...")
            print()
            continue

        print("\nAgente: ", end="", flush=True)
        result = agent.run(user_input)
        print(result.answer)

        if result.tools_used:
            print(f"  ↳ Herramientas: {', '.join(result.tools_used)} · {result.steps} pasos")
        print()


if __name__ == "__main__":
    main()
