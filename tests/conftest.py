import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models
from app.db.postgres import Base
import app.db.postgres as dbp
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def _configure_test_db():
    # Use in-memory SQLite for fast, isolated tests
    test_db_url = "sqlite+pysqlite:///:memory:"
    engine = create_engine(test_db_url, future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    # Rebind the application's DB session/engine to the test DB
    dbp.engine = engine
    dbp.SessionLocal = TestingSessionLocal

    # Create all tables once for the session
    Base.metadata.create_all(engine)

    yield

    # Teardown (drop all tables)
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db_session():
    db = dbp.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    return TestClient(app)
