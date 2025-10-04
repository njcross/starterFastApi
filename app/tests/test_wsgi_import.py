# app/tests/test_wsgi_import.py
def test_wsgi_import_loads_app():
    from app import wsgi
    assert hasattr(wsgi, "app")
    assert wsgi.app is not None
