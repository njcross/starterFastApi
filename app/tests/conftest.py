import os
import pytest
import fakeredis

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# set DB to sqlite before importing app
os.environ["ENV"] = "test"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["BACKEND_PUBLIC_URL"] = "http://localhost:8000"
os.environ["FRONTEND_URL"] = "http://localhost:5173"
os.environ["MAGIC_TOKEN_TTL"] = "900"
os.environ["SESSION_TTL_DAYS"] = "1"
os.environ["ENV_NAME"] = "test"

from app.main import app
from app.db import get_db
from app.models import Base
from app.core.redis_client import get_redis
from fastapi.testclient import TestClient

# --- DB setup for tests (SQLite in-memory shared) ---
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

TEST_ENGINE = create_engine(
    os.environ["DATABASE_URL"],
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,         # ← single shared in-memory DB
    future=True,
)
TestingSessionLocal = sessionmaker(bind=TEST_ENGINE, autoflush=False, autocommit=False, future=True)

@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)

@pytest.fixture
def db_session_factory():
    return TestingSessionLocal

@pytest.fixture(autouse=True)
def _override_db_dep():
    def _get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.pop(get_db, None)

# --- Redis override ---
@pytest.fixture(scope="session")
def fake_redis():
    import fakeredis
    return fakeredis.FakeRedis(decode_responses=True)

@pytest.fixture(autouse=True)
def _override_redis(fake_redis):
    app.dependency_overrides[get_redis] = lambda: fake_redis
    yield
    app.dependency_overrides.pop(get_redis, None)


@pytest.fixture
def client(fake_redis, db_session_factory):
    from app.db import get_db
    from app.core.redis_client import get_redis
    from app.auth import deps as auth_deps
    from fastapi.testclient import TestClient
    from app.main import app

    # --- DB override ---
    def _get_db():
        db = db_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db

    # --- Redis overrides (belt & suspenders) ---
    # Some routes import get_redis from core, others via auth.deps.
    app.dependency_overrides[get_redis] = lambda: fake_redis
    app.dependency_overrides[auth_deps.get_redis] = lambda: fake_redis

    with TestClient(app) as c:
        yield c

    # clean up
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_redis, None)
    app.dependency_overrides.pop(auth_deps.get_redis, None)

# Helper to create a user and set sid cookie in the TestClient
@pytest.fixture()
def login_user(db_session_factory, fake_redis):
    from app.models.user import User
    from sqlalchemy import select
    from app.auth.session import create_session

    def _login(email="test@example.com", client: TestClient | None = None):
        db = db_session_factory()
        try:
            u = db.scalar(select(User).where(User.email == email))
            if not u:
                u = User(email=email)
                db.add(u)
                db.commit()
                db.refresh(u)
        finally:
            db.close()

        sid = create_session(u.id, r=fake_redis)  # use the SAME fake redis
        if client is not None:
            client.cookies.set("sid", sid)
        return u, sid

    return _login
