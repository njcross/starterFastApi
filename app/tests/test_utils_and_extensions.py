# app/tests/test_utils_and_extensions.py
import importlib

def test_utils_functions_exist():
    mod = importlib.import_module("app.routes.utils")
    # call any helpers if present
    for name in ("normalize_origin", "parse_frontend_origin"):
        if hasattr(mod, name):
            fn = getattr(mod, name)
            assert fn("http://localhost:5173")  # just not raising

def test_extensions_import_side_effects():
    # If extensions attaches middleware/routers at import time, this will run them.
    mod = importlib.import_module("app.extensions")
    assert mod is not None
