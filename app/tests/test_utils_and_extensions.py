# app/tests/test_utils_and_extensions.py
import importlib

def test_extensions_import_side_effects():
    # If extensions attaches middleware/routers at import time, this will run them.
    mod = importlib.import_module("app.extensions")
    assert mod is not None
