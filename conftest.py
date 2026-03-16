"""
conftest.py
-----------
pytest fixtures and hooks shared by all test modules.

LEARNING NOTE — Fixtures
  A fixture is a function that sets something up before a test and
  tears it down after.  Tests declare what they need in their parameters:

      def test_login(driver):         # gets a fresh browser
      def test_dashboard(admin_driver): # gets a logged-in admin browser

  scope="function" means a new driver is created for every test.
  This prevents tests from sharing state (the #1 cause of flaky tests).

LEARNING NOTE — yield
  Everything before yield = SETUP
  Everything after yield  = TEARDOWN (runs even if the test fails)
"""
import pytest
import allure

from utils.driver_factory import DriverFactory
from utils.screenshot_utils import take_screenshot, attach_page_source
from utils.logger import get_logger
from config.settings import ADMIN_EMAIL, ADMIN_PASSWORD, USER_EMAIL, USER_PASSWORD

logger = get_logger("conftest")


# ── Raw driver fixture ─────────────────────────────────────────────────────────
@pytest.fixture(scope="function")
def driver():
    """Fresh WebDriver for one test. Quits after test finishes."""
    drv = DriverFactory.get_driver()
    logger.info("Driver created")
    yield drv
    drv.quit()
    logger.info("Driver quit")


# ── Pre-logged-in fixtures ─────────────────────────────────────────────────────
@pytest.fixture(scope="function")
def admin_driver(driver):
    """Driver already authenticated as admin@example.com."""
    from pages.login_page import LoginPage
    lp = LoginPage(driver)
    lp.open_login()
    lp.login(ADMIN_EMAIL, ADMIN_PASSWORD)
    # Wait for dashboard to confirm login succeeded
    from pages.dashboard_page import DashboardPage
    DashboardPage(driver).is_loaded()
    logger.info(f"Admin session ready: {ADMIN_EMAIL}")
    return driver


@pytest.fixture(scope="function")
def user_driver(driver):
    """Driver already authenticated as a normal (non-admin) user."""
    from pages.login_page import LoginPage
    lp = LoginPage(driver)
    lp.open_login()
    lp.login(USER_EMAIL, USER_PASSWORD)
    logger.info(f"User session ready: {USER_EMAIL}")
    return driver


# ── Screenshot on failure ──────────────────────────────────────────────────────
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    After the test body runs ('call' phase), if it failed:
      1. Take a screenshot
      2. Attach page HTML
      3. Log the failure

    LEARNING NOTE:
      hookwrapper=True lets us intercept the test result.
      tryfirst=True ensures our hook runs before pytest's own reporting,
      so the screenshot is available when the report is generated.
    """
    outcome = yield
    report  = outcome.get_result()

    if report.when == "call" and report.failed:
        # Try all driver fixture names
        drv = (item.funcargs.get("driver")
               or item.funcargs.get("admin_driver")
               or item.funcargs.get("user_driver"))

        if drv:
            name = item.name.replace("[", "_").replace("]", "").replace(" ", "_")
            take_screenshot(drv, f"FAIL_{name}")
            attach_page_source(drv, f"source_{name}")
            logger.error(f"FAILED: {item.name}")


# ── CLI option ─────────────────────────────────────────────────────────────────
def pytest_addoption(parser):
    parser.addoption(
        "--browser", action="store", default="chrome",
        help="Browser: chrome | firefox"
    )
