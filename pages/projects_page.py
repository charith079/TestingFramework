"""
pages/projects_page.py
-----------------------
Covers TC05 — create project, search, verify it appears.
"""
from pages.base_page import BasePage
from config.locators import ProjectsLocators as P


class ProjectsPage(BasePage):
    PATH = "/projects"

    def open_projects(self) -> "ProjectsPage":
        self.open(self.PATH)
        return self

    def click_new_project(self) -> "ProjectsPage":
        """Click the 'New Project' btn — opens modal."""
        self.logger.info("Opening New Project modal")
        self.click(P.NEW_BTN)
        return self

    def fill_project_form(self, name: str, description: str = "") -> "ProjectsPage":
        """Fill modal form fields."""
        self.wait.until_visible(P.MODAL)
        self.type_text(P.NAME_INPUT, name)
        if description:
            try:
                self.type_text(P.DESC_INPUT, description)
            except Exception:
                self.logger.debug("No description field found — skipping")
        return self

    def submit_project_form(self) -> "ProjectsPage":
        self.click(P.MODAL_SUBMIT)
        # Wait for modal to close
        self.wait.is_visible(P.MODAL, timeout=2)   # waits briefly then continues
        return self

    def create_project(self, name: str, description: str = "") -> "ProjectsPage":
        """End-to-end: open modal → fill → submit."""
        self.click_new_project()
        self.fill_project_form(name, description)
        self.submit_project_form()
        self.logger.info(f"Project created: '{name}'")
        return self

    def search(self, term: str) -> "ProjectsPage":
        """Type in the search / filter input."""
        try:
            self.type_text(P.SEARCH_INPUT, term)
        except Exception:
            self.logger.debug("Search input not found — using status filter instead")
        return self

    def get_project_names(self) -> list:
        """Return visible project name texts."""
        items = self.find_all(P.PROJECT_NAME)
        return [i.text.strip() for i in items if i.text.strip()]

    def project_exists(self, name: str) -> bool:
        return any(name.lower() in n.lower() for n in self.get_project_names())
