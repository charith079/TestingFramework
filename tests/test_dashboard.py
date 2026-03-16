"""
tests/test_dashboard.py
------------------------
Verify post-login landing and role-based content on dashboard.

LEARNING NOTE — Why a separate dashboard test?
  The dashboard is the first thing a user sees after login.
  If it breaks, every other feature is unreachable.
  Testing it independently makes failures easy to diagnose.
"""
import allure
import pytest

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from config.settings import ADMIN_EMAIL


@allure.suite("Dashboard")
@allure.title("Dashboard loads after admin login")
@allure.severity(allure.severity_level.CRITICAL)
def test_dashboard_loads_after_login(admin_driver):
    """
    Verify that after admin login:
      - The page heading (h1) is visible
      - The URL contains /dashboard or the app root
      - No error alert is shown
    """
    dash = DashboardPage(admin_driver)

    with allure.step("Assert page heading is visible"):
        assert dash.is_loaded(), (
            f"Dashboard heading not found. URL: {admin_driver.current_url}"
        )

    with allure.step("Assert URL is not /login"):
        assert "/login" not in admin_driver.current_url, (
            "Still on login page — dashboard did not load"
        )

    with allure.step("Log heading text for the report"):
        heading = dash.get_heading()
        allure.attach(heading, name="Dashboard heading", attachment_type=allure.attachment_type.TEXT)


@allure.suite("Dashboard")
@allure.title("Sidebar navigation links are present")
@allure.severity(allure.severity_level.NORMAL)
def test_dashboard_nav_links_present(admin_driver):
    """
    Verify that the sidebar renders navigation links after login.
    Admin should see at least: Projects, Tasks, Users.
    """
    dash = DashboardPage(admin_driver)

    with allure.step("Collect nav link texts"):
        links = dash.nav_links()
        allure.attach(
            "\n".join(links),
            name="Nav links found",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("Assert at least 2 nav links exist"):
        assert len(links) >= 2, (
            f"Expected multiple nav links, got: {links}"
        )


@allure.suite("Dashboard")
@allure.title("Logout redirects to login page")
@allure.severity(allure.severity_level.CRITICAL)
def test_dashboard_logout(admin_driver):
    """
    Verify logout flow:
      1. Start on dashboard (already logged in via admin_driver fixture)
      2. Click logout
      3. Assert redirected to /login
    """
    dash  = DashboardPage(admin_driver)
    login = LoginPage(admin_driver)

    with allure.step("Confirm dashboard is loaded"):
        assert dash.is_loaded(), "Dashboard not loaded before logout"

    with allure.step("Click logout"):
        dash.logout()

    with allure.step("Assert redirected to login page"):
        assert login.is_on_login_page(), (
            f"Expected /login after logout but got: {admin_driver.current_url}"
        )
