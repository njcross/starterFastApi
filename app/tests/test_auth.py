from urllib.parse import urlparse

def test_request_link_creates_user_and_responds(client, db_session_factory):
    res = client.post("/api/auth/request-link", json={"email": "newuser@example.com"})
    assert res.status_code == 200
    assert res.json()["sent"] is True

    # user was created
    from app.models.user import User
    db = db_session_factory()
    try:
        u = db.query(User).filter(User.email == "newuser@example.com").first()
        assert u is not None
    finally:
        db.close()


def test_protected_route_requires_login(client):
    res = client.get("/api/protected/whoami")
    assert res.status_code == 401


def test_protected_route_with_login(client, login_user):
    user, sid = login_user("me@example.com", client=client)
    res = client.get("/api/protected/whoami")
    assert res.status_code == 200
    assert res.json()["user_id"] == user.id

def test_callback_sets_cookie_and_redirects(client, fake_redis, db_session_factory):
    from app.models.user import User
    db = db_session_factory()
    try:
        u = User(email="cb@example.com")
        db.add(u)
        db.commit()
        db.refresh(u)
    finally:
        db.close()

    token = "TESTTOKEN"
    fake_redis.setex(f"magic:{token}", 900, str(u.id))

    res = client.get(f"/api/auth/callback?token={token}", follow_redirects=False)
    assert res.status_code in (302, 303)
    assert "sid=" in res.headers.get("set-cookie", "")



def test_logout_clears_session(client, login_user):
    user, sid = login_user("bye@example.com", client=client)
    # sanity check: me works
    me1 = client.get("/api/auth/me").json()
    assert me1["user"]["email"] == "bye@example.com"

    r = client.post("/api/auth/logout")
    assert r.status_code == 200

    # cookie cleared & session gone
    me2 = client.get("/api/auth/me").json()
    assert me2 == {'detail': 'Unauthorized'}
