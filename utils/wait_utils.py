"""
utils/wait_utils.py
-------------------
Explicit-wait helpers used across all page objects.

LEARNING NOTE — Why explicit waits?
  time.sleep(3) always wastes 3 seconds even if the element appeared in 0.2s.
  WebDriverWait polls every 500ms and returns the moment the condition is met.
  Maximum wait = timeout; average wait = much less.

  Rule: NEVER use time.sleep() in this framework. Use these helpers instead.

Usage:
  wait = WaitHelper(driver)
  btn = wait.until_clickable(ProjectsLocators.NEW_BTN)
  btn.click()
"""
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from config.settings import DEFAULT_WAIT


class WaitHelper:

    def __init__(self, driver: WebDriver, timeout: int = DEFAULT_WAIT):
        self.driver  = driver
        self.timeout = timeout

    def _wait(self, timeout=None) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout or self.timeout)

    # ── Visibility ─────────────────────────────────────────────────────────────
    def until_visible(self, locator: tuple, timeout: int = None) -> WebElement:
        """Wait until element exists in DOM AND is visible on screen."""
        return self._wait(timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def until_present(self, locator: tuple, timeout: int = None) -> WebElement:
        """Wait until element is in DOM (may still be hidden)."""
        return self._wait(timeout).until(
            EC.presence_of_element_located(locator)
        )

    def until_all_present(self, locator: tuple, timeout: int = None):
        """Wait until at least one element matching locator is in DOM."""
        return self._wait(timeout).until(
            EC.presence_of_all_elements_located(locator)
        )

    # ── Clickability ───────────────────────────────────────────────────────────
    def until_clickable(self, locator: tuple, timeout: int = None) -> WebElement:
        """Wait until element is visible AND enabled (safe to click)."""
        return self._wait(timeout).until(
            EC.element_to_be_clickable(locator)
        )

    # ── URL / Title ────────────────────────────────────────────────────────────
    def until_url_contains(self, partial: str, timeout: int = None) -> bool:
        return self._wait(timeout).until(EC.url_contains(partial))

    def until_title_contains(self, partial: str, timeout: int = None) -> bool:
        return self._wait(timeout).until(EC.title_contains(partial))

    # ── Alerts ─────────────────────────────────────────────────────────────────
    def until_alert(self, timeout: int = None):
        """Return the Alert object once a JS dialog is present."""
        return self._wait(timeout).until(EC.alert_is_present())

    # ── Windows ────────────────────────────────────────────────────────────────
    def until_new_window(self, current_count: int, timeout: int = None) -> bool:
        """Wait until the number of open windows increases by 1."""
        return self._wait(timeout).until(
            EC.number_of_windows_to_be(current_count + 1)
        )

    # ── Frame ──────────────────────────────────────────────────────────────────
    def until_frame_and_switch(self, locator: tuple, timeout: int = None):
        """Wait for iframe to be available, then switch into it."""
        return self._wait(timeout).until(
            EC.frame_to_be_available_and_switch_to_it(locator)
        )

    # ── Text ───────────────────────────────────────────────────────────────────
    def until_text_in(self, locator: tuple, text: str, timeout: int = None) -> bool:
        return self._wait(timeout).until(
            EC.text_to_be_present_in_element(locator, text)
        )

    # ── Staleness ──────────────────────────────────────────────────────────────
    def until_stale(self, element: WebElement, timeout: int = None) -> bool:
        return self._wait(timeout).until(EC.staleness_of(element))

    # ── Safe check (no exception) ──────────────────────────────────────────────
    def is_visible(self, locator: tuple, timeout: int = 3) -> bool:
        """Returns True/False — never raises. Use for conditional assertions."""
        try:
            self.until_visible(locator, timeout)
            return True
        except TimeoutException:
            return False

    def is_present(self, locator: tuple, timeout: int = 3) -> bool:
        try:
            self.until_present(locator, timeout)
            return True
        except TimeoutException:
            return False
