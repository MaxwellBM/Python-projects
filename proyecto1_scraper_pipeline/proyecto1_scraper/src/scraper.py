"""
scraper.py — Extrae datos de quotes.toscrape.com (sitio de práctica legal)
"""

import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from typing import Optional
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str] = field(default_factory=list)
    author_url: Optional[str] = None


class QuoteScraper:
    """Scraper OOP para extraer quotes con paginación."""

    def __init__(self, base_url: str = BASE_URL, delay: float = 1.0):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (educational scraper)"})

    def _get_page(self, url: str) -> Optional[BeautifulSoup]:
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            logger.error(f"Error al obtener {url}: {e}")
            return None

    def _parse_quotes(self, soup: BeautifulSoup) -> list[Quote]:
        quotes = []
        for item in soup.select(".quote"):
            text = item.select_one(".text").get_text(strip=True).strip('""\u201c\u201d')
            author = item.select_one(".author").get_text(strip=True)
            tags = [t.get_text(strip=True) for t in item.select(".tag")]
            author_link = item.select_one("a[href*='/author/']")
            author_url = self.base_url + author_link["href"] if author_link else None
            quotes.append(Quote(text=text, author=author, tags=tags, author_url=author_url))
        return quotes

    def _get_next_page(self, soup: BeautifulSoup) -> Optional[str]:
        next_btn = soup.select_one("li.next a")
        return self.base_url + next_btn["href"] if next_btn else None

    def scrape(self, max_pages: int = 3) -> list[Quote]:
        all_quotes = []
        url = self.base_url
        page = 1

        while url and page <= max_pages:
            logger.info(f"Scrapeando página {page}: {url}")
            soup = self._get_page(url)
            if not soup:
                break
            quotes = self._parse_quotes(soup)
            all_quotes.extend(quotes)
            logger.info(f"  -> {len(quotes)} quotes encontradas")
            url = self._get_next_page(soup)
            page += 1
            time.sleep(self.delay)

        logger.info(f"Total: {len(all_quotes)} quotes extraídas")
        return all_quotes


if __name__ == "__main__":
    scraper = QuoteScraper()
    quotes = scraper.scrape(max_pages=2)
    for q in quotes[:3]:
        print(f"\n'{q.text[:60]}...' — {q.author}")
        print(f"  Tags: {', '.join(q.tags)}")
