"""Pytest Configuration and Fixtures.

Configures an isolated SQLite test database and an HTTPX TestClient for API testing.
Ensures zero pollution of development data and guaranteed test database cleanup.
"""

import sys
from pathlib import Path
from typing import Generator
import pytest

# Ensure backend root is in Python module search path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.camera.camera_client import camera_client
from app.camera.camera_state import camera_state
from app.core.config import get_settings
from app.db.base import Base
import app.models  # Ensure all domain models are registered with Base.metadata
from app.db.session import get_db
from app.main import app
from app.services.telemetry_state import telemetry_state_service
from app.vision.model_registry import set_active_provider

TEST_DB_PATH = Path(__file__).resolve().parent / "test_pipebot.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test database schema and clean up artifacts after all tests run."""
    # Ensure any previous artifact is removed
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Provide an isolated database session for a test function."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Provide a TestClient with overridden get_db dependency pointing to the test database."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_telemetry_and_devices():
    """Guarantee isolated in-memory telemetry, camera, and inference state between tests."""
    telemetry_state_service.reset()
    camera_state.reset()
    camera_client.frame_reader.reset_queue()
    set_active_provider(None)
    yield
    telemetry_state_service.reset()
    camera_state.reset()
    camera_client.frame_reader.reset_queue()
    set_active_provider(None)

