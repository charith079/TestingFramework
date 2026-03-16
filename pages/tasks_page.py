"""
pages/tasks_page.py
--------------------
Covers TC06 — change task status and verify it persists after refresh.
"""
from selenium.webdriver.support.ui import Select
from pages.base_page import BasePage
from config.locators import TasksLocators as T


class TasksPage(BasePage):
    PATH = "/tasks"

    def open_tasks(self) -> "TasksPage":
        self.open(self.PATH)
        return self

    def get_row_count(self) -> int:
        return len(self.find_all(T.TABLE_ROWS))

    def update_first_task_status(self, new_status: str) -> "TasksPage":
        """
        Find the first task row, locate its status <select>, change the value.

        LEARNING NOTE — Select helper:
          selenium.webdriver.support.ui.Select wraps a <select> element and
          gives you select_by_value(), select_by_visible_text(), etc.
        """
        rows = self.find_all(T.TABLE_ROWS)
        if not rows:
            self.logger.warning("No task rows found")
            return self

        first_row = rows[0]

        # Try finding an edit button first
        try:
            edit_btn = first_row.find_element(*T.EDIT_BTN)
            edit_btn.click()
            self.logger.info("Clicked edit button on first task")
        except Exception:
            self.logger.debug("No edit button in row — attempting inline select")

        # Locate the status <select> (may be on the row or in an opened form)
        try:
            selects = self.driver.find_elements(*T.STATUS_SELECT)
            if selects:
                sel = Select(selects[0])
                sel.select_by_value(new_status)
                self.logger.info(f"Status changed → '{new_status}'")
            else:
                self.logger.warning("No status <select> found on tasks page")
        except Exception as exc:
            self.logger.error(f"Could not update status: {exc}")

        # Save if a save/submit button is visible
        try:
            saves = self.driver.find_elements(*T.SAVE_BTN)
            if saves:
                saves[0].click()
                self.logger.info("Clicked save button")
        except Exception:
            pass

        return self

    def get_first_task_status(self) -> str:
        """Read the current status text/badge from the first task row."""
        rows = self.find_all(T.TABLE_ROWS)
        if not rows:
            return ""
        try:
            badge = rows[0].find_element(*T.STATUS_BADGE)
            return badge.text.strip()
        except Exception:
            return ""

    def refresh_and_get_first_status(self) -> str:
        self.refresh()
        return self.get_first_task_status()
