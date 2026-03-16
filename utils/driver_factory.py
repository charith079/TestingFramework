"""
utils/driver_factory.py
-----------------------
Builds WebDriver instances for local or Selenium Grid execution.

Follows your exact class pattern with two private factory methods:
  _create_local_driver()   — chromedriver / geckodriver on this machine
  _create_remote_driver()  — Selenium Grid via RemoteWebDriver

LEARNING NOTE — Why a Factory class?
  Tests never call webdriver.Chrome() directly.
  All driver setup lives here, so switching browsers or adding Grid
  support is a one-file change, not a change across every test.
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from config.settings import BROWSER, EXECUTION_MODE, GRID_URL, HEADLESS, PAGE_LOAD_WAIT


class DriverFactory:

    @staticmethod
    def get_driver() -> webdriver.Remote:
        """
        Entry point called by conftest.py.
        Decides local vs remote based on EXECUTION_MODE setting.
        """
        if EXECUTION_MODE == "remote":
            return DriverFactory._create_remote_driver()
        return DriverFactory._create_local_driver()

    # ── Local ─────────────────────────────────────────────────────────────────
    @staticmethod
    def _create_local_driver():
        """Spin up a driver directly on this machine."""
        if BROWSER == "chrome":
            options = DriverFactory._chrome_options()
            driver = webdriver.Chrome(options=options)

        elif BROWSER == "firefox":
            options = DriverFactory._firefox_options()
            driver = webdriver.Firefox(options=options)

        else:
            raise Exception(f"Unsupported browser: '{BROWSER}'. Use 'chrome' or 'firefox'.")

        driver.maximize_window()
        driver.set_page_load_timeout(PAGE_LOAD_WAIT)
        driver.implicitly_wait(0)   # explicit waits only — never mix with implicit
        return driver

    # ── Remote (Selenium Grid) ────────────────────────────────────────────────
    @staticmethod
    def _create_remote_driver():
        """
        Connect to the Selenium Grid hub.
        The hub distributes sessions across the 3 registered nodes automatically.

        LEARNING NOTE:
          webdriver.Remote() takes a command_executor (hub URL) and options.
          The options object carries the browserName capability so the hub
          picks a matching node.
        """
        if BROWSER == "chrome":
            options = DriverFactory._chrome_options()

        elif BROWSER == "firefox":
            options = DriverFactory._firefox_options()

        else:
            raise Exception(f"Unsupported browser: '{BROWSER}'. Use 'chrome' or 'firefox'.")

        driver = webdriver.Remote(
            command_executor=GRID_URL,
            options=options
        )

        driver.maximize_window()
        driver.set_page_load_timeout(PAGE_LOAD_WAIT)
        driver.implicitly_wait(0)   # explicit waits only
        return driver

    # ── Option builders ───────────────────────────────────────────────────────
    @staticmethod
    def _chrome_options() -> ChromeOptions:
        opts = ChromeOptions()
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--disable-extensions")
        if HEADLESS:
            opts.add_argument("--headless=new")     # Chrome 112+ flag
        return opts

    @staticmethod
    def _firefox_options() -> FirefoxOptions:
        opts = FirefoxOptions()
        if HEADLESS:
            opts.add_argument("--headless")
        return opts
