"""
utils/screenshot_utils.py
--------------------------
Saves PNG screenshots and attaches them to the Allure report.
Called automatically by conftest.py on every test failure.

LEARNING NOTE:
  allure.attach() embeds the image directly into the HTML report so you
  can see exactly what the browser showed when the test failed — no
  manual file hunting needed.
"""
import allure
from datetime import datetime
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver
from config.settings import SCREENSHOTS_DIR
from utils.logger import get_logger

logger = get_logger(__name__)


def take_screenshot(driver: WebDriver, name: str = "screenshot") -> Path:
    """
    Capture the current browser state as PNG.
    Saves to reports/screenshots/ and attaches to Allure report.
    Returns the file path.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename  = f"{name}_{timestamp}.png"
    filepath  = SCREENSHOTS_DIR / filename

    try:
        driver.save_screenshot(str(filepath))
        logger.info(f"Screenshot → {filepath.name}")

        with open(filepath, "rb") as f:
            allure.attach(
                f.read(),
                name=name,
                attachment_type=allure.attachment_type.PNG
            )
    except Exception as exc:
        logger.warning(f"Screenshot failed: {exc}")

    return filepath


def attach_page_source(driver: WebDriver, name: str = "page_source"):
    """Attach the raw page HTML to Allure — helps debug locator failures."""
    try:
        allure.attach(
            driver.page_source,
            name=name,
            attachment_type=allure.attachment_type.HTML
        )
    except Exception as exc:
        logger.warning(f"Page source attach failed: {exc}")
