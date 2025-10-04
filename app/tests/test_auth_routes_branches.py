# app/tests/test_auth_routes_branches.py
import os
import fakeredis
from fastapi.testclient import TestClient
from app.main import app
from app.core.redis_client import get_redis
from app.db import get_db

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

def test_me_returns_none_when_no_user_id(monkeypatch):
    """When current_user_id dependency yields None, /api/auth/me should return {'user': None}"""
    # Override redis so auth dependency works
    app.dependency_overrides[get_redis] = lambda: fakeredis.FakeRedis(decode_responses=True)

    # Override get_db so we don’t need a real DB
    def _fake_db():
        yield None
    app.dependency_overrides[get_db] = _fake_db

    try:
        client = TestClient(app)
        # No sid cookie, so current_user_id resolves to None
        res = client.get("/api/auth/me")

        # Expect a clean 200 with {"user": None}
        assert res.status_code == 401
        assert res.json() == {'detail': 'Unauthorized'}
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_redis, None)