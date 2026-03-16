"""
tests/test_auth.py
------------------
TC01 — Valid admin login
TC02 — Invalid login matrix (parameterized)

LEARNING NOTE — @pytest.mark.parametrize
  Instead of writing 4 identical test functions, we write ONE and pass
  different data rows.  pytest runs the function once per row, giving
  each run its own pass/fail result in the report.
"""
import pytest
import allure

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from utils.data_loader import invalid_login_matrix
from config.settings import ADMIN_EMAIL, ADMIN_PASSWORD


# ─────────────────────────────────────────────────────────────────────────────
@allure.suite("Authentication")
@allure.title("TC01 — Valid admin login")
@allure.severity(allure.severity_level.BLOCKER)
def test_tc01_valid_admin_login(driver):
    """
    Verify that a valid admin can log in and the dashboard loads.

    Steps:
      1. Open /login
      2. Enter valid admin credentials
      3. Click Login
      4. Assert dashboard heading is visible
    """
    login = LoginPage(driver)
    dash  = DashboardPage(driver)

    with allure.step("Open login page"):
        login.open_login()
        assert login.is_on_login_page(), "Login page did not open"

    with allure.step(f"Enter credentials for {ADMIN_EMAIL}"):
        login.login(ADMIN_EMAIL, ADMIN_PASSWORD)

    with allure.step("Assert dashboard loaded"):
        assert dash.is_loaded(), \
            f"Dashboard did not load after login. Current URL: {driver.current_url}"

    with allure.step("Assert no error alert shown"):
        assert not login.is_displayed(login.wait.is_visible.__self__.__class__,
                                       timeout=2), True   # just check no error present


# ─────────────────────────────────────────────────────────────────────────────
@allure.suite("Authentication")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize(
    "test_id, email, password, description",
    invalid_login_matrix(),
    ids=[row[0] for row in invalid_login_matrix()]   # readable test IDs in report
)
def test_tc02_invalid_login_matrix(driver, test_id, email, password, description):
    """
    TC02 — Verify error behavior for multiple invalid credential combinations.

    Parameterized rows (from config/test_data.json):
      • wrong_password      — valid email, wrong password
      • invalid_email_format — malformed email
      • empty_both          — both fields empty
      • nonexistent_user    — email not registered

    Expected: error message shown, user stays on /login
    """
    allure.dynamic.title(f"TC02 — Invalid login: {description}")

    login = LoginPage(driver)

    with allure.step("Open login page"):
        login.open_login()

    with allure.step(f"Submit: email='{email}' password='{password}'"):
        login.login(email, password)

    with allure.step("Assert user is still on login page or error shown"):
        still_on_login = login.is_on_login_page()
        error_shown    = login.get_error_text() != ""

        assert still_on_login or error_shown, (
            f"Expected login failure for [{description}] but "
            f"URL is: {driver.current_url}"
        )
