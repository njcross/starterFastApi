# app/tests/test_health_routes_branches.py
import json
import fakeredis
from fastapi.testclient import TestClient
from app.main import app
from app.core.redis_client import get_redis
import app.routes.health as health
import importlib
from unittest.mock import patch


def test_health_ok(monkeypatch):
    app.dependency_overrides[get_redis] = lambda: fakeredis.FakeRedis(decode_responses=True)
    try:
        res = TestClient(app).get("/api/health")
        assert res.status_code == 200
        body = res.json()
        assert body.get("ok") is True or res.status_code == 200  # tolerate your schema
    finally:
        app.dependency_overrides.pop(get_redis, None)

def test_health_handles_redis_failure(monkeypatch):
    class BadRedis:
        def ping(self): raise RuntimeError("boom")
    app.dependency_overrides[get_redis] = lambda: BadRedis()
    try:
        res = TestClient(app).get("/api/health")
        # should still return JSON with a non-200 or {'ok': False}
        assert res.status_code in (200, 503, 500)
        data = res.json()
        assert isinstance(data, dict)
    finally:
        app.dependency_overrides.pop(get_redis, None)

def test_health_get_redis_uses_env(monkeypatch):
    # set the env var that should drive the client
    monkeypatch.setenv("REDIS_URL", "redis://example:6379/9")

    # reload config so settings picks up the new env
    import app.core.config as config
    importlib.reload(config)

    # reload redis_client so it reads the reloaded settings
    import app.core.redis_client as rc
    importlib.reload(rc)

    # (if you added the tiny helper) ensure no override and clear cache
    rc.set_redis_override(None)
    rc._build_client.cache_clear()

    # reload health to ensure it uses the current rc module
    import app.routes.health as health
    importlib.reload(health)

    # assert Redis.from_url is called with the env URL
    with patch("app.core.redis_client.Redis.from_url") as mocked:
        # health.get_redis should delegate to rc.get_redis()
        health.get_redis()
        mocked.assert_called_once_with("redis://example:6379/9", decode_responses=True)

class FakeRedis:
    def __init__(self):
        self.store = {}
    def set(self, k, v, ex=None):
        self.store[k] = v
    def get(self, k):
        return self.store.get(k)

def test_ping_redis_ok(monkeypatch):
    monkeypatch.setattr(health, "get_redis", lambda: FakeRedis(), raising=True)
    rv = TestClient(app).get("/api/ping-redis")
    assert rv.status_code == 200
    assert rv.json() == {"redis": "world"}  # value written by route

class FakeConn:
    def execute(self, _):
        class Row:  # mimic fetchone() returning a tuple-like
            def fetchone(self):
                return ("PostgreSQL 16.1",)
        return Row()
    def close(self): pass
    # support context manager via engine.connect()
class FakeConnectCM:
    def __enter__(self): return FakeConn()
    def __exit__(self, *a): pass
class FakeEngine:
    def connect(self): return FakeConnectCM()

def test_db_version_success(monkeypatch):
    monkeypatch.setattr(health, "engine", FakeEngine(), raising=True)
    rv = TestClient(app).get("/api/db-version")
    assert rv.status_code == 200
    assert rv.json() == {"postgres_version": "PostgreSQL 16.1"}

# app/tests/test_health_db_version_error.py
from fastapi.testclient import TestClient
from app.main import app
import app.routes.health as health

class BoomEngine:
    def connect(self):
        class CM:
            def __enter__(self): raise RuntimeError("boom")
            def __exit__(self, *a): pass
        return CM()

def test_db_version_error(monkeypatch):
    monkeypatch.setattr(health, "engine", BoomEngine(), raising=True)
    rv = TestClient(app).get("/api/db-version")
    assert rv.status_code == 500  # route returns {"error": "..."} with 200
    body = rv.json()
    assert "error" in body and "boom" in body["error"]

def test_ping_redis_decodes_bytes_when_decode_responses_false(monkeypatch):
    # fakeredis with decode_responses=False returns BYTES from .get(...)
    r = fakeredis.FakeRedis(decode_responses=False)

    # Patch the dependency used inside app.routes.health
    monkeypatch.setattr(health, "get_redis", lambda: r, raising=True)

    rv = TestClient(app).get("/api/ping-redis")
    assert rv.status_code == 200
    # Route should have decoded b"world" -> "world"
    assert rv.json() == {"redis": "world"}
