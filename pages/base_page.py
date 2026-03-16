"""
pages/base_page.py
------------------
BasePage provides reusable browser actions for every page object.

LEARNING NOTE — Page Object Model (POM)
  Each page in the app gets its own Python class.
  The class exposes high-level methods like login(), create_project().
  Tests call those methods — they never touch CSS selectors directly.

  Benefits:
    ✓ Selector change → fix in one file, not every test
    ✓ Tests read like plain English
    ✓ Reuse: 10 tests that need login all call the same login() method
"""
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from config.settings import BASE_URL
from utils.wait_utils import WaitHelper
from utils.logger import get_logger
from utils.screenshot_utils import take_screenshot


class BasePage:

    def __init__(self, driver: WebDriver):
        self.driver   = driver
        self.wait     = WaitHelper(driver)
        self.logger   = get_logger(self.__class__.__name__)
        self.base_url = BASE_URL

    # ── Navigation ─────────────────────────────────────────────────────────────
    def open(self, path: str = "") -> None:
        url = f"{self.base_url}{path}"
        self.logger.info(f"GET {url}")
        self.driver.get(url)

    @property
    def current_url(self) -> str:
        return self.driver.current_url

    @property
    def title(self) -> str:
        return self.driver.title

    # ── Element actions ────────────────────────────────────────────────────────
    def click(self, locator: tuple) -> None:
        el = self.wait.until_clickable(locator)
        self.logger.debug(f"click  {locator[1]}")
        el.click()

    def type_text(self, locator: tuple, text: str, clear: bool = True) -> None:
        el = self.wait.until_visible(locator)
        if clear:
            el.clear()
        self.logger.debug(f"type   {locator[1]} → '{text}'")
        el.send_keys(text)

    def get_text(self, locator: tuple) -> str:
        return self.wait.until_visible(locator).text.strip()

    def is_displayed(self, locator: tuple, timeout: int = 5) -> bool:
        return self.wait.is_visible(locator, timeout)

    def find(self, locator: tuple) -> WebElement:
        return self.wait.until_present(locator)

    def find_all(self, locator: tuple) -> list:
        """Return list of elements; empty list if none found (no exception)."""
        try:
            return self.wait.until_all_present(locator)
        except Exception:
            return []

    def refresh(self) -> None:
        self.logger.info("Refreshing page")
        self.driver.refresh()

    # ── Screenshot ─────────────────────────────────────────────────────────────
    def screenshot(self, name: str = "page") -> None:
        take_screenshot(self.driver, name)
