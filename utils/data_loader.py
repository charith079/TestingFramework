"""
utils/data_loader.py
---------------------
Loads test data from config/test_data.json.

LEARNING NOTE:
  Keeping data in JSON (not hardcoded in tests) means:
  - Non-engineers can update test values without reading Python
  - Same data file can be used for multiple test runs / environments
"""
import json
from pathlib import Path

_DATA_FILE = Path(__file__).resolve().parent.parent / "config" / "test_data.json"


def load_all() -> dict:
    with open(_DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def get(key: str):
    return load_all()[key]


def invalid_login_matrix():
    """
    Returns list of (test_id, email, password, description) tuples
    ready for @pytest.mark.parametrize.
    """
    rows = get("invalid_login_matrix")
    return [(r["id"], r["email"], r["password"], r["desc"]) for r in rows]
