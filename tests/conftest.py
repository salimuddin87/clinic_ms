# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# import app and DB utilities
from app import main as app_main
from app import database, models
from app import auth as auth_mod

# Create an in-memory sqlite engine that can be shared across threads
TEST_SQLITE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in test DB
models.Base.metadata.create_all(bind=engine)


# Dependency override for get_db used by routers
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def setup_db():
    # nothing else required here because tables already created above
    yield
    # optional: drop all tables after test session
    models.Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    """Yield a DB session for direct DB access in tests if needed."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(monkeypatch, setup_db):
    """
    Provides a TestClient with dependency overrides so the app uses the in-memory DB.
    """
    # override the database.get_db used in routers
    monkeypatch.setattr(database, "SessionLocal", TestingSessionLocal, raising=False)
    # override the generator function in database module if imported directly by routers
    app_main.app.dependency_overrides[database.get_db] = override_get_db
    # auth module also defines its own get_db; override that too
    try:
        app_main.app.dependency_overrides[auth_mod.get_db] = override_get_db
    except Exception:
        # if auth.get_db not present or imported differently, ignore
        pass

    client = TestClient(app_main.app)
    yield client

    # cleanup dependency overrides
    app_main.app.dependency_overrides.clear()
