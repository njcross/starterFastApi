# app/tests/test_redis_client_module.py
import os
import fakeredis
from app.core import redis_client as rc
import importlib
from unittest.mock import patch

def test_get_redis_uses_override(monkeypatch):
    fake = fakeredis.FakeRedis(decode_responses=True)
    # monkeypatch the module-level client and ensure get_redis returns it
    monkeypatch.setattr(rc, "redis_client", fake, raising=True)
    out = rc.get_redis()
    assert out is fake


def test_from_url_called_on_import(monkeypatch):
    monkeypatch.setenv("REDIS_URL", "redis://example:6379/9")

    import app.core.config as config
    importlib.reload(config)
    import app.core.redis_client as rc
    importlib.reload(rc)

    rc._build_client.cache_clear()  # clear any prior cache
    with patch("app.core.redis_client.Redis.from_url") as mocked:
        rc.get_redis()
        mocked.assert_called_once_with("redis://example:6379/9", decode_responses=True)

def test_set_redis_override_clears_and_rebuilds(monkeypatch):
    import app.core.redis_client as rc
    from unittest.mock import MagicMock

    # 1️⃣ Set an override
    fake = fakeredis.FakeRedis(decode_responses=True)
    rc.set_redis_override(fake)
    assert rc.get_redis() is fake  # override used

    # 2️⃣ Patch Redis.from_url to see if it's called after clearing
    mock_from_url = MagicMock(return_value="NEW_CLIENT")
    monkeypatch.setattr(rc, "Redis", type("R", (), {"from_url": staticmethod(mock_from_url)}))

    # 3️⃣ Clear override (client=None should trigger cache_clear)
    rc.set_redis_override(None)

    # 4️⃣ Call get_redis() again → should rebuild via Redis.from_url
    out = rc.get_redis()
    mock_from_url.assert_called_once_with(rc.settings.REDIS_URL, decode_responses=True)
    assert out == "NEW_CLIENT"
