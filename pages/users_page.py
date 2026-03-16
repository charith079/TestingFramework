"""
pages/users_page.py
--------------------
Covers TC03 (admin sees table) and TC04 (non-admin sees warning).
"""
from pages.base_page import BasePage
from config.locators import UsersLocators as U


class UsersPage(BasePage):
    PATH = "/users"

    def open_users(self) -> "UsersPage":
        self.open(self.PATH)
        return self

    # ── Admin assertions ───────────────────────────────────────────────────────
    def is_table_visible(self) -> bool:
        return self.is_displayed(U.TABLE, timeout=8)

    def get_row_count(self) -> int:
        rows = self.find_all(U.TABLE_ROWS)
        return len(rows)

    # ── Non-admin assertions ───────────────────────────────────────────────────
    def is_access_denied_shown(self) -> bool:
        """
        The app renders a Bootstrap alert-warning with text
        "You don't have permission to access this page."
        for non-admin users.
        """
        return self.is_displayed(U.ACCESS_DENIED, timeout=8)

    def get_access_denied_text(self) -> str:
        if self.is_access_denied_shown():
            return self.get_text(U.ACCESS_DENIED)
        return ""
