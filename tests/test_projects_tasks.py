"""
tests/test_projects_tasks.py
-----------------------------
TC05 — Create a project and verify it appears in the list
TC06 — Change a task's status and confirm it persists after page refresh

LEARNING NOTE — Test Independence
  Each test starts from a known state (fresh login via admin_driver).
  TC05 does not depend on TC06, and vice versa.
  Tests that share state break silently — always start clean.
"""
import allure
import pytest

from pages.projects_page import ProjectsPage
from pages.tasks_page import TasksPage
from utils.data_loader import get


# ─────────────────────────────────────────────────────────────────────────────
@allure.suite("Projects & Tasks")
@allure.title("TC05 — Create project and verify in list")
@allure.severity(allure.severity_level.CRITICAL)
def test_tc05_create_project(admin_driver):
    """
    Verify a user can create a new project and it appears in the project list.

    Steps:
      1. Open /projects
      2. Click 'New Project' button
      3. Fill in project name and description
      4. Submit the form
      5. Search for the created project
      6. Assert it appears in results

    Test data from config/test_data.json → "new_project"
    """
    project_data = get("new_project")
    name         = project_data["name"]
    description  = project_data["description"]

    projects = ProjectsPage(admin_driver)

    with allure.step("Navigate to Projects page"):
        projects.open_projects()

    with allure.step(f"Create project: '{name}'"):
        projects.create_project(name, description)

    with allure.step("Search for the newly created project"):
        projects.search(name)

    with allure.step("Assert project appears in the list"):
        assert projects.project_exists(name), (
            f"Project '{name}' not found in project list after creation.\n"
            f"Visible projects: {projects.get_project_names()}"
        )

    allure.attach(
        f"Name: {name}\nDescription: {description}",
        name="Created project data",
        attachment_type=allure.attachment_type.TEXT
    )


# ─────────────────────────────────────────────────────────────────────────────
@allure.suite("Projects & Tasks")
@allure.title("TC06 — Task status update persists after refresh")
@allure.severity(allure.severity_level.CRITICAL)
def test_tc06_task_status_update(admin_driver):
    """
    Verify that changing a task's status is persisted.

    Steps:
      1. Open /tasks
      2. Record the current status of the first task
      3. Change its status via the <select> dropdown
      4. Save
      5. Refresh the page
      6. Confirm the new status is still shown

    LEARNING NOTE — Select element:
      selenium.webdriver.support.ui.Select wraps a <select> tag.
      .select_by_value("in_progress") chooses the <option value="in_progress">.
    """
    new_status = get("task_status_new")       # "in_progress" from test_data.json
    tasks = TasksPage(admin_driver)

    with allure.step("Navigate to Tasks page"):
        tasks.open_tasks()

    with allure.step("Assert at least one task exists"):
        count = tasks.get_row_count()
        assert count >= 1, "No tasks found on the Tasks page — cannot run TC06"

    with allure.step(f"Change first task status to '{new_status}'"):
        tasks.update_first_task_status(new_status)

    with allure.step("Refresh page and read status"):
        status_after_refresh = tasks.refresh_and_get_first_status()
        allure.attach(
            f"Expected status: {new_status}\nActual after refresh: {status_after_refresh}",
            name="Status comparison",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("Assert status persisted"):
        # Status text may be displayed as a badge label, so check case-insensitively
        assert new_status.lower().replace("_", " ") in status_after_refresh.lower().replace("_", " ") \
               or new_status.lower() in status_after_refresh.lower(), (
            f"Status after refresh '{status_after_refresh}' does not match "
            f"expected '{new_status}'"
        )
