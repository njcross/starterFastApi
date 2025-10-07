# tests/test_auth_callback_json.py
import fakeredis
from fastapi.testclient import TestClient
from app.main import app
from app.core.redis_client import get_redis

def _seed_token(token: str, user_id: str = "1"):
    r = fakeredis.FakeRedis(decode_responses=True)
    r.setex(f"magic:{token}", 900, user_id)
    app.dependency_overrides[get_redis] = lambda: r
    return r

def test_callback_json_via_accept_header(monkeypatch):
    _seed_token("tok_json_accept")
    monkeypatch.setenv("ENV_NAME", "test")  # ensures Secure not forced
    client = TestClient(app)

    resp = client.get(
        "/api/auth/callback?token=tok_json_accept",
        headers={"Accept": "application/json"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True and "next" in body
    assert "sid=" in resp.headers.get("set-cookie", "")

    app.dependency_overrides.pop(get_redis, None)

def test_callback_json_via_query_flag(monkeypatch):
    _seed_token("tok_json_flag")
    monkeypatch.setenv("ENV_NAME", "test")
    client = TestClient(app)

    resp = client.get("/api/auth/callback?token=tok_json_flag&json=1")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True and "next" in body
    assert "sid=" in resp.headers.get("set-cookie", "")

    app.dependency_overrides.pop(get_redis, None)

