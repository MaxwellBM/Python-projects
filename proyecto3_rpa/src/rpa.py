"""
rpa.py — Automatización RPA con Selenium: login, navegación y extracción de datos
Sitio de práctica: https://the-internet.herokuapp.com
"""

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = "https://the-internet.herokuapp.com"
SCREENSHOTS_DIR = Path("screenshots")


@dataclass
class LoginResult:
    success: bool
    message: str
    username: str = ""


@dataclass
class TableRow:
    last_name: str
    first_name: str
    email: str
    due: str
    web_site: str
    action: str


class RPABot:
    """
    Bot RPA que automatiza tareas en un sitio web de práctica:
    - Login con credenciales
    - Extracción de tablas
    - Interacción con formularios
    - Capturas de pantalla como evidencia
    """

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        SCREENSHOTS_DIR.mkdir(exist_ok=True)

    def _build_driver(self) -> webdriver.Chrome:
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1280,900")
        options.add_argument("--disable-gpu")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
        )
        return webdriver.Chrome(options=options)

    def __enter__(self) -> "RPABot":
        self.driver = self._build_driver()
        self.wait = WebDriverWait(self.driver, timeout=10)
        logger.info("WebDriver iniciado")
        return self

    def __exit__(self, *args) -> None:
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver cerrado")

    # ── Utilidades ────────────────────────────────────────────────────────────

    def screenshot(self, name: str) -> Path:
        path = SCREENSHOTS_DIR / f"{name}_{int(time.time())}.png"
        self.driver.save_screenshot(str(path))
        logger.info(f"Screenshot guardado: {path}")
        return path

    def _find(self, by: By, selector: str, timeout: int = 10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )

    def _click(self, by: By, selector: str) -> None:
        el = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((by, selector))
        )
        el.click()

    # ── Tareas RPA ────────────────────────────────────────────────────────────

    def login(self, username: str, password: str) -> LoginResult:
        """Tarea 1: Login en formulario de autenticación."""
        try:
            self.driver.get(f"{BASE_URL}/login")
            self._find(By.ID, "username").send_keys(username)
            self._find(By.ID, "password").send_keys(password)
            self._click(By.CSS_SELECTOR, "button[type='submit']")

            # Verificar resultado
            try:
                flash = self._find(By.ID, "flash", timeout=5)
                text = flash.text.lower()
                if "you logged into a secure area" in text:
                    self.screenshot("login_success")
                    return LoginResult(success=True, message="Login exitoso", username=username)
                else:
                    self.screenshot("login_failed")
                    return LoginResult(success=False, message=flash.text.strip())
            except TimeoutException:
                return LoginResult(success=False, message="No se encontró mensaje de respuesta")

        except WebDriverException as e:
            logger.error(f"Error en login: {e}")
            return LoginResult(success=False, message=str(e))

    def extract_table(self) -> list[TableRow]:
        """Tarea 2: Extrae datos de una tabla HTML dinámica."""
        try:
            self.driver.get(f"{BASE_URL}/tables")
            table = self._find(By.CSS_SELECTOR, "#table1 tbody")
            rows = []
            for tr in table.find_elements(By.TAG_NAME, "tr"):
                cols = [td.text.strip() for td in tr.find_elements(By.TAG_NAME, "td")]
                if len(cols) >= 6:
                    rows.append(TableRow(*cols[:6]))
            logger.info(f"Extraídas {len(rows)} filas de la tabla")
            self.screenshot("table_extracted")
            return rows
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Error extrayendo tabla: {e}")
            return []

    def handle_alerts(self) -> dict:
        """Tarea 3: Interactúa con alerts de JavaScript."""
        results = {}
        try:
            self.driver.get(f"{BASE_URL}/javascript_alerts")

            # Alert simple
            self._click(By.XPATH, "//button[text()='Click for JS Alert']")
            alert = self.driver.switch_to.alert
            results["alert_text"] = alert.text
            alert.accept()

            # Confirm
            self._click(By.XPATH, "//button[text()='Click for JS Confirm']")
            confirm = self.driver.switch_to.alert
            results["confirm_text"] = confirm.text
            confirm.accept()

            # Prompt
            self._click(By.XPATH, "//button[text()='Click for JS Prompt']")
            prompt = self.driver.switch_to.alert
            results["prompt_text"] = prompt.text
            prompt.send_keys("Automatizado con Selenium")
            prompt.accept()

            result_el = self._find(By.ID, "result")
            results["prompt_result"] = result_el.text
            self.screenshot("alerts_handled")
            logger.info(f"Alerts manejados: {results}")

        except Exception as e:
            logger.error(f"Error en alerts: {e}")
            results["error"] = str(e)

        return results

    def download_report(self, output_path: Path = Path("data/report.txt")) -> bool:
        """Tarea 4: Navega, extrae contenido y lo guarda como reporte."""
        try:
            self.driver.get(f"{BASE_URL}/dynamic_content")
            output_path.parent.mkdir(parents=True, exist_ok=True)

            items = self.driver.find_elements(By.CSS_SELECTOR, "#content .row")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("REPORTE AUTOMÁTICO — Dynamic Content\n")
                f.write("=" * 50 + "\n\n")
                for i, item in enumerate(items, 1):
                    try:
                        text = item.find_element(By.TAG_NAME, "div").text.strip()
                        if text:
                            f.write(f"[{i}] {text}\n\n")
                    except NoSuchElementException:
                        continue

            logger.info(f"Reporte guardado: {output_path}")
            self.screenshot("report_downloaded")
            return True

        except Exception as e:
            logger.error(f"Error generando reporte: {e}")
            return False

    def run_full_pipeline(self) -> dict:
        """Ejecuta todas las tareas RPA en secuencia."""
        results = {}

        logger.info("── Tarea 1: Login ──")
        login = self.login("tomsmith", "SuperSecretPassword!")
        results["login"] = {"success": login.success, "message": login.message}

        logger.info("── Tarea 2: Extracción de tabla ──")
        rows = self.extract_table()
        results["table"] = {"rows_extracted": len(rows), "sample": vars(rows[0]) if rows else {}}

        logger.info("── Tarea 3: Manejo de alerts ──")
        results["alerts"] = self.handle_alerts()

        logger.info("── Tarea 4: Descarga de reporte ──")
        results["report"] = {"saved": self.download_report()}

        return results


if __name__ == "__main__":
    import json
    with RPABot(headless=True) as bot:
        results = bot.run_full_pipeline()
    print("\n📋 Resultados:")
    print(json.dumps(results, indent=2, ensure_ascii=False))
