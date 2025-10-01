import os
import pytest
import fakeredis
from app import create_app
from app.extensions import db as _db
from flask import current_app

@pytest.fixture(scope="session")
def app():
    os.environ["ENV"] = "test"
    # Your app reads DATABASE_URL; keep using that for tests
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["REDIS_URL"] = "redis://localhost:6379/0"
    os.environ["BACKEND_PUBLIC_URL"] = "http://localhost:8000"
    os.environ["FRONTEND_URL"] = "http://localhost:5173"
    os.environ["MAGIC_TOKEN_TTL"] = "900"
    os.environ["SESSION_TTL_DAYS"] = "1"

    app = create_app()
    with app.app_context():
        _db.create_all()
        app.redis = fakeredis.FakeRedis(decode_responses=True)
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def login_user(app):
    """Helper to create a user and set a sid cookie on the client."""
    from app.models import User
    from app.extensions import db
    from app.auth.session import create_session

    def _login(client, email="test@example.com"):
        with app.app_context():                         # ← ensure app ctx
            u = User.query.filter_by(email=email).first()
            if not u:
                u = User(email=email)
                db.session.add(u)
                db.session.commit()
            sid = create_session(u.id)
        client.set_cookie("sid", sid) 
        return u, sid

    return _login
