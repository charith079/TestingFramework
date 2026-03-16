"""
pages/login_page.py
-------------------
Encapsulates everything on the /login page.
"""
from pages.base_page import BasePage
from config.locators import LoginLocators as L


class LoginPage(BasePage):
    PATH = "/login"

    def open_login(self) -> "LoginPage":
        self.open(self.PATH)
        return self

    def enter_email(self, email: str) -> "LoginPage":
        self.type_text(L.EMAIL, email)
        return self

    def enter_password(self, password: str) -> "LoginPage":
        self.type_text(L.PASSWORD, password)
        return self

    def click_login(self) -> "LoginPage":
        self.click(L.SUBMIT)
        return self

    def login(self, email: str, password: str) -> "LoginPage":
        """Convenience: fill both fields and submit in one call."""
        self.logger.info(f"Logging in as '{email}'")
        self.enter_email(email)
        self.enter_password(password)
        self.click_login()
        return self

    def get_error_text(self) -> str:
        """Return the Bootstrap alert text shown on bad credentials."""
        if self.is_displayed(L.ERROR_ALERT, timeout=5):
            return self.get_text(L.ERROR_ALERT)
        return ""

    def is_on_login_page(self) -> bool:
        return "/login" in self.current_url or self.is_displayed(L.SUBMIT, timeout=3)

    def is_login_failed(self) -> bool:
        """True when the error alert appeared AND we're still on /login."""
        return self.is_displayed(L.ERROR_ALERT, timeout=5) or self.is_on_login_page()
