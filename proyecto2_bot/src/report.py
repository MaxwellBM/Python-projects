"""
report.py — Genera mensajes de texto con estadísticas para enviar por Telegram
"""

from db import Storage


class ReportGenerator:
    def __init__(self, storage: Storage):
        self.db = storage

    def _no_data(self) -> str:
        return "⚠️ No hay datos disponibles. Ejecuta el pipeline primero:\n`cd ../proyecto1 && python src/main.py`"

    def resumen(self) -> str:
        if not self.db.db_exists():
            return self._no_data()

        total = self.db.total_quotes()
        authors = self.db.unique_authors()
        avg = self.db.avg_words()
        top = self.db.top_authors(limit=1)
        top_author = top.iloc[0]["author"] if not top.empty else "N/A"

        return (
            "📊 *Resumen del Dataset*\n"
            "─────────────────────\n"
            f"📝 Total quotes:    *{total}*\n"
            f"👤 Autores únicos:  *{authors}*\n"
            f"📏 Palabras promedio: *{avg}*\n"
            f"🏆 Autor más citado: *{top_author}*\n"
            "─────────────────────\n"
            "_Datos extraídos con el scraper ETL_"
        )

    def top_autores(self) -> str:
        if not self.db.db_exists():
            return self._no_data()

        df = self.db.top_authors(limit=5)
        if df.empty:
            return "No hay datos de autores."

        lines = ["👤 *Top 5 Autores*\n─────────────────────"]
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        for i, row in df.iterrows():
            medal = medals[i] if i < len(medals) else "▪️"
            lines.append(f"{medal} {row['author']} — *{row['quotes']}* quotes")
        return "\n".join(lines)

    def top_tags(self) -> str:
        if not self.db.db_exists():
            return self._no_data()

        df = self.db.top_tags(limit=8)
        if df.empty:
            return "No hay datos de tags."

        lines = ["🏷️ *Top Tags*\n─────────────────────"]
        col = df.columns[-1]
        for _, row in df.iterrows():
            tag = row.iloc[0]
            count = row[col]
            bar = "█" * min(int(count), 10)
            lines.append(f"`{tag:<18}` {bar} {count}")
        return "\n".join(lines)

    def buscar_autor(self, name: str) -> str:
        if not self.db.db_exists():
            return self._no_data()

        df = self.db.search_author(name)
        if df.empty:
            return f"❌ No se encontraron quotes de *{name}*."

        lines = [f"🔍 *Quotes de {df.iloc[0]['author']}*\n"]
        for _, row in df.iterrows():
            text = row["text"][:120] + ("..." if len(row["text"]) > 120 else "")
            lines.append(f"_\"{text}\"_\n")
        return "\n".join(lines)
