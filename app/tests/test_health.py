import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c

def test_health(client):
    rv = client.get("/api/health")
    assert rv.status_code == 200
    data = rv.json()
    assert isinstance(data, dict)
    assert data.get("ok") is True

@pytest.mark.integration
def test_ping_redis_integration(client):
    if not os.environ.get("REDIS_URL"):
        pytest.skip("REDIS_URL not set; skipping integration test")
    rv = client.get("/api/ping-redis")
    assert rv.status_code == 200
    data = rv.json()
    assert "redis" in data

@pytest.mark.integration
def test_db_version_integration(client):
    if not os.environ.get("DATABASE_URL") and not os.environ.get("POSTGRES_USER"):
        pytest.skip("DB env not set; skipping integration test")
    rv = client.get("/api/db-version")
    assert rv.status_code == 200
    data = rv.json()
    assert "postgres_version" in data or "error" in data
