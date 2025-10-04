# app/tests/test_db_dependency.py
from app.db import get_db
# app/tests/test_auth_routes_branches.py
import os
import fakeredis
from fastapi.testclient import TestClient
from app.main import app
from app.core.redis_client import get_redis

def test_callback_invalid_token_returns_400(monkeypatch):
    app.dependency_overrides[get_redis] = lambda: fakeredis.FakeRedis(decode_responses=True)
    try:
        res = TestClient(app).get("/api/auth/callback?token=doesnotexist")
        assert res.status_code == 400
        assert {'error': 'invalid or expired token'} == res.json()
    finally:
        app.dependency_overrides.pop(get_redis, None)

def test_callback_sets_secure_cookie_in_prod_env(monkeypatch):
    r = fakeredis.FakeRedis(decode_responses=True)
    r.setex("magic:tok", 900, "123")
    app.dependency_overrides[get_redis] = lambda: r
    # force non-test env to exercise secure=True branch
    monkeypatch.setenv("ENV_NAME", "prod")
    try:
        client = TestClient(app)
        res = client.get("/api/auth/callback?token=tok", follow_redirects=False)
        assert res.status_code in (302, 303)
        # Cookie header should include "Secure" in prod
        cookie_header = res.headers.get("set-cookie", "")
        assert "sid=" in cookie_header
        assert "Secure" in cookie_header
    finally:
        app.dependency_overrides.pop(get_redis, None)
        monkeypatch.setenv("ENV_NAME", "test")


def test_get_db_yields_and_closes():
    gen = get_db()
    db = next(gen)
    # Do something trivial: query connection works
    assert db.bind is not None
    # Finish generator -> trigger close()
    try:
        next(gen)
    except StopIteration:
        pass
    # Session closed: new op should open a new connection (no exception thrown)
    # just ensure calling close() twice is safe
    db.close()