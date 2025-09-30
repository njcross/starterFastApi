import os
import json
import pytest

# Import the Flask application factory
from app import create_app

@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client

def test_health(client):
    rv = client.get('/api/health')
    assert rv.status_code == 200
    data = rv.get_json()
    assert isinstance(data, dict)
    assert data.get('ok') is True

@pytest.mark.integration
def test_ping_redis_integration(client):
    # This test will pass if Redis is reachable (dev compose up), otherwise it gets skipped
    if not os.environ.get("REDIS_URL"):
        pytest.skip("REDIS_URL not set; skipping integration test")
    rv = client.get('/api/ping-redis')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'redis' in data

@pytest.mark.integration
def test_db_version_integration(client):
    if not os.environ.get("DATABASE_URL") and not os.environ.get("POSTGRES_USER"):
        pytest.skip("DB env not set; skipping integration test")
    rv = client.get('/api/db-version')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'postgres_version' in data or 'error' in data
