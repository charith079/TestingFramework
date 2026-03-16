"""
tests/test_access_control.py
-----------------------------
TC03 — Admin can access the Users page (sees the table)
TC04 — Non-admin is blocked with a permission warning

LEARNING NOTE — Access Control Testing
  These tests use TWO different fixtures:
    admin_driver  → logged in as admin@example.com
    user_driver   → logged in as a normal user

  Same URL, different sessions, different expected outcomes.
  This is a core pattern in role-based access control (RBAC) testing.

Real app behaviour (confirmed from HTML):
  Non-admin sees:
    <div role="alert" class="fade alert alert-warning show">
      You don't have permission to access this page.
    </div>
"""
import allure
import pytest

from pages.users_page import UsersPage
from pages.dashboard_page import DashboardPage


# ─────────────────────────────────────────────────────────────────────────────
@allure.suite("Access Control")
@allure.title("TC03 — Admin can access Users page")
@allure.severity(allure.severity_level.CRITICAL)
def test_tc03_admin_users_page_access(admin_driver):
    """
    Verify admin can open /users and see the users table.

    Steps:
      1. Login as admin (handled by admin_driver fixture)
      2. Navigate to /users
      3. Assert the data table is visible
      4. Assert at least 1 row exists
    """
    users = UsersPage(admin_driver)

    with allure.step("Navigate to /users as admin"):
        users.open_users()

    with allure.step("Assert users table is visible"):
        assert users.is_table_visible(), (
            f"Users table not found on {admin_driver.current_url}. "
            "Admin should see the full users table."
        )

    with allure.step("Assert table has at least 1 row"):
        row_count = users.get_row_count()
        allure.attach(
            str(row_count),
            name="User row count",
            attachment_type=allure.attachment_type.TEXT
        )
        assert row_count >= 1, "Users table appears empty — expected at least 1 user row"


# ─────────────────────────────────────────────────────────────────────────────
@allure.suite("Access Control")
@allure.title("TC04 — Non-admin cannot access Users page")
@allure.severity(allure.severity_level.CRITICAL)
def test_tc04_non_admin_access_restriction(user_driver):
    """
    Verify a normal user is blocked from /users with a permission warning.

    Expected:
      Bootstrap alert-warning:
      "You don't have permission to access this page."

    Steps:
      1. Login as normal user (handled by user_driver fixture)
      2. Navigate directly to /users
      3. Assert the permission denied alert is shown
      4. Assert the users table is NOT shown
    """
    users = UsersPage(user_driver)

    with allure.step("Navigate to /users as normal user"):
        users.open_users()

    with allure.step("Assert permission denied warning is shown"):
        assert users.is_access_denied_shown(), (
            f"Expected access-denied alert at {user_driver.current_url} "
            "for non-admin user, but it was not shown."
        )

    with allure.step("Log the access denied message text"):
        msg = users.get_access_denied_text()
        allure.attach(msg, name="Access denied message", attachment_type=allure.attachment_type.TEXT)
        assert "permission" in msg.lower(), (
            f"Alert text '{msg}' does not mention permission"
        )

    with allure.step("Assert users table is NOT visible"):
        assert not users.is_table_visible(), (
            "Users table should not be visible to a non-admin user"
        )
