# UI Automation Level 2 — Selenium + Python

Automated test framework for [react-frontend-api-testing.vercel.app](https://react-frontend-api-testing.vercel.app)

---

## Framework Structure

```
ui-automation-level2/
├── tests/                          # Test files (one per module)
│   ├── test_auth.py                # TC01, TC02 — Login tests
│   ├── test_dashboard.py           # Dashboard + logout
│   ├── test_access_control.py      # TC03, TC04 — Role-based access
│   ├── test_projects_tasks.py      # TC05, TC06 — Projects & tasks
│   └── test_browser_interactions.py # TC07, TC08 — Alerts, iFrame, windows
│
├── pages/                          # Page Object Model classes
│   ├── base_page.py                # Shared browser actions
│   ├── login_page.py
│   ├── dashboard_page.py
│   ├── users_page.py
│   ├── projects_page.py
│   ├── tasks_page.py
│   └── test_scenarios_page.py
│
├── utils/                          # Reusable utilities
│   ├── driver_factory.py           # Local + Grid WebDriver creation
│   ├── wait_utils.py               # All explicit wait helpers
│   ├── logger.py                   # Console + rotating file logger
│   ├── screenshot_utils.py         # PNG capture + Allure attachment
│   └── data_loader.py              # JSON test data reader
│
├── config/                         # All config in one place
│   ├── settings.py                 # Env-var based configuration
│   ├── locators.py                 # ALL CSS/XPath selectors
│   ├── test_data.json              # Test credentials and inputs
│   └── grid_config.json            # Grid node configuration
│
├── reports/
│   ├── allure-results/             # Allure raw results
│   ├── screenshots/                # Failure screenshots
│   └── junit.xml                   # CI-compatible XML report
│
├── logs/
│   └── automation.log              # Rotating log file
│
├── conftest.py                     # Shared fixtures + failure hook
├── pytest.ini                      # pytest configuration
├── docker-compose.yml              # Selenium Grid (hub + 3 nodes)
└── requirements.txt
```

---

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Create a `.env` file (optional — overrides defaults)

```env
BASE_URL=https://react-frontend-api-testing.vercel.app
BROWSER=chrome
HEADLESS=false
EXECUTION_MODE=remote
GRID_URL=http://localhost:4444/wd/hub
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=Admin@123
USER_EMAIL=user@example.com
USER_PASSWORD=User@123
```

---

## Running Tests

### Option A — Local execution (no Grid)

```bash
EXECUTION_MODE=local pytest
```

### Option B — Single test by name

```bash
EXECUTION_MODE=local pytest tests/test_auth.py::test_tc01_valid_admin_login -v
```

### Option C — Selenium Grid (3 parallel nodes)

**Step 1: Start the Grid**
```bash
docker-compose up -d
```

**Step 2: Wait ~15 seconds, then verify nodes registered**
```
http://localhost:4444/ui
```
You should see 3 Chrome nodes with status "UP".

**Step 3: Run tests in parallel across 3 nodes**
```bash
pytest -n 3 --dist=loadscope \
       --alluredir=reports/allure-results \
       --junitxml=reports/junit.xml
```

**Step 4: Stop the Grid**
```bash
docker-compose down
```

### Option D — Headless CI execution

```bash
HEADLESS=true EXECUTION_MODE=remote \
pytest -n 3 --dist=loadscope \
       --alluredir=reports/allure-results \
       --junitxml=reports/junit.xml
```

---

## Allure Report

```bash
# Generate and open HTML report
allure serve reports/allure-results

# Or generate static HTML
allure generate reports/allure-results -o reports/allure-html --clean
allure open reports/allure-html
```

---

## Test Cases

| ID    | File                          | Description                              | Fixture      |
|-------|-------------------------------|------------------------------------------|--------------|
| TC01  | test_auth.py                  | Valid admin login                        | driver       |
| TC02  | test_auth.py                  | Invalid login matrix (4 parameterized)   | driver       |
| TC03  | test_access_control.py        | Admin accesses Users page                | admin_driver |
| TC04  | test_access_control.py        | Non-admin blocked from Users page        | user_driver  |
| TC05  | test_projects_tasks.py        | Create project + verify in list          | admin_driver |
| TC06  | test_projects_tasks.py        | Update task status + verify after refresh| admin_driver |
| TC07  | test_browser_interactions.py  | Alert / Confirm / Prompt dialogs         | admin_driver |
| TC08  | test_browser_interactions.py  | iFrame + new tab + popup window          | admin_driver |

---

## Key Design Decisions

| Decision | Why |
|---|---|
| Page Object Model | Selector changes = 1-line fix, not 20 test edits |
| Explicit waits only | No `time.sleep()` — faster and more reliable |
| `driver_factory.py` | Tests never import `webdriver` directly |
| Fixtures in conftest | Fresh browser per test — no shared state |
| Screenshot on failure | Attached to Allure automatically — no manual hunting |
| Env-var config | Same code runs locally, on Grid, and in CI |
| `test_data.json` | Non-engineers can update test data without reading Python |

---

## Troubleshooting

**`SessionNotCreatedException` on Grid** — nodes not ready yet. Wait 20s after `docker-compose up`.

**`TimeoutException`** — page loaded slowly. Increase `DEFAULT_WAIT` env var: `DEFAULT_WAIT=15 pytest`

**`NoSuchElementException` on modal** — modal animation still playing. The `wait.until_visible()` handles this but you can increase `DEFAULT_WAIT` if on a slow connection.

**`NoAlertPresentException`** — alert was handled before the test got to it. Always trigger alerts fresh within each test — never share state between tests.
