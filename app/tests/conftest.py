# app/tests/conftest.py
import os
import pytest
from app import create_app
from app.extensions import db as _db

@pytest.fixture(scope="session")
def app():
    os.environ["DATABASE_URL"] = "postgresql+psycopg://postgres:postgres@localhost:5432/appdb_test"
    app = create_app()
    with app.app_context():
        _db.drop_all()
        _db.create_all()
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()