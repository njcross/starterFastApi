# app/tests/test_deps.py
import pytest
import fakeredis

from fastapi.testclient import TestClient
from app.main import app
from app.core.redis_client import get_redis  # <-- this is the real dependency

@pytest.fixture(autouse=True)
def _fake_redis():
    r = fakeredis.FakeRedis(decode_responses=True)
    app.dependency_overrides[get_redis] = lambda: r
    yield
    app.dependency_overrides.pop(get_redis, None)

def test_current_user_id_no_cookie_returns_401(client: TestClient):
    res = client.get("/api/auth/me")
    assert res.status_code == 401

def test_current_user_id_handles_redis_error(client: TestClient):
    class Boom:
        def get(self, *_args, **_kwargs):
            raise RuntimeError("boom")

    # Override the actual dependency FastAPI injects into current_user_id
    app.dependency_overrides[get_redis] = lambda: Boom()
    try:
        r = client.get("/api/auth/me")
        assert r.status_code == 401
        assert r.json() == {"detail": "Unauthorized"}
    finally:
        app.dependency_overrides.pop(get_redis, None)

# app/tests/test_deps.py
import pytest
import fakeredis

from fastapi.testclient import TestClient
from app.main import app
from app.core.redis_client import get_redis  # <-- this is the real dependency

@pytest.fixture(autouse=True)
def _fake_redis():
    r = fakeredis.FakeRedis(decode_responses=True)
    app.dependency_overrides[get_redis] = lambda: r
    yield
    app.dependency_overrides.pop(get_redis, None)

def test_current_user_id_no_cookie_returns_401(client: TestClient):
    res = client.get("/api/auth/me")
    assert res.status_code == 401

def test_current_user_id_handles_redis_error(client: TestClient):
    class Boom:
        def get(self, *_args, **_kwargs):
            raise RuntimeError("boom")

    # Override the actual dependency FastAPI injects into current_user_id
    app.dependency_overrides[get_redis] = lambda: Boom()
    try:
        r = client.get("/api/auth/me")
        assert r.status_code == 401
        assert r.json() == {"detail": "Unauthorized"}
    finally:
        app.dependency_overrides.pop(get_redis, None)
