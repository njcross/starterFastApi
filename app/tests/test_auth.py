# app/tests/test_auth.py
from urllib.parse import urlparse
from app.models import User

def test_request_link_creates_user_and_responds(client, app):
    res = client.post("/api/auth/request-link", json={"email": "newuser@example.com"})
    assert res.status_code == 200
    assert res.get_json()["sent"] is True

    # user was created
    with app.app_context():
        u = User.query.filter_by(email="newuser@example.com").first()
        assert u is not None

def test_callback_sets_cookie_and_redirects(client, app):
    # Arrange: create user & put a fake magic token in redis
    with app.app_context():
        u = User(email="cb@example.com")
        from app.extensions import db
        db.session.add(u); db.session.commit()
        token = "TESTTOKEN"
        app.redis.setex(f"magic:{token}", 900, str(u.id))

    # Act: hit callback
    res = client.get(f"/api/auth/callback?token={token}", follow_redirects=False)

    # Assert: redirect to FRONTEND_URL and Set-Cookie contains sid
    assert res.status_code in (302, 303)
    loc = res.headers.get("Location")
    assert loc and urlparse(loc).netloc in ("localhost:5173", "localhost")

    set_cookie = res.headers.get("Set-Cookie", "")
    assert "sid=" in set_cookie

def test_protected_route_requires_login(client):
    res = client.get("/api/protected/whoami")
    assert res.status_code == 401

def test_protected_route_with_login(client, login_user):
    user, sid = login_user(client, "me@example.com")
    res = client.get("/api/protected/whoami")
    assert res.status_code == 200
    assert res.get_json()["user_id"] == user.id
