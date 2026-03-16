"""
pages/dashboard_page.py
------------------------
Post-login landing page checks and navigation helpers.
"""
from pages.base_page import BasePage
from config.locators import DashboardLocators as D, NavLocators as N


class DashboardPage(BasePage):
    PATH = "/dashboard"

    def is_loaded(self) -> bool:
        """True once the page heading renders — confirms successful login."""
        return self.is_displayed(D.HEADING, timeout=10)

    def get_heading(self) -> str:
        return self.get_text(D.HEADING)

    def get_user_info(self) -> str:
        """Return any role/username text visible in the navbar."""
        if self.is_displayed(N.USER_INFO, timeout=4):
            return self.get_text(N.USER_INFO)
        return ""

    def logout(self) -> None:
        """Click the logout link/button."""
        self.logger.info("Logging out")
        if self.is_displayed(N.LOGOUT, timeout=4):
            self.click(N.LOGOUT)
        else:
            # Fallback: direct navigation
            self.open("/logout")

    def go_to(self, path: str) -> None:
        """Navigate to any app path via address bar (bypasses nav clicks)."""
        self.open(path)

    def nav_links(self) -> list:
        """Return list of all sidebar nav link text values."""
        links = self.find_all(N.ALL_NAV_LINKS)
        return [l.text.strip() for l in links if l.text.strip()]
