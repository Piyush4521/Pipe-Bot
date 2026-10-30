"""Comprehensive Test Suite for Health, Readiness, and System Status Endpoints."""

from datetime import datetime
from unittest.mock import MagicMock
from fastapi import status
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app


def test_root_endpoint(client: TestClient):
    """Verify application identity response on GET /."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["app"] == "PipeBot Backend"
    assert "version" in data
    assert data["status"] == "running"
    assert data["docs_url"] == "/docs"
    assert data["api_prefix"] == "/api/v1"


def test_health_endpoint(client: TestClient):
    """Verify general application health on GET /api/v1/health."""
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "PipeBot Backend"
    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data
    assert "timestamp" in data
    # Assert ISO 8601 parseable timestamp
    parsed_time = datetime.fromisoformat(data["timestamp"])
    assert parsed_time is not None


def test_readiness_probe_healthy(client: TestClient):
    """Verify readiness probe on GET /api/v1/health/ready when database is accessible."""
    response = client.get("/api/v1/health/ready")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] is True
    assert "timestamp" in data


def test_database_health_endpoint(client: TestClient):
    """Verify database ping and latency reporting on GET /api/v1/health/database."""
    response = client.get("/api/v1/health/database")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "connected"
    assert data["database_type"] == "sqlite"
    assert isinstance(data["response_time_ms"], (int, float))
    assert data["response_time_ms"] >= 0


def test_system_status_contract_and_disconnected_defaults(client: TestClient):
    """Verify system status conforms to frontend contract with authentic disconnected hardware states."""
    response = client.get("/api/v1/system/status")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Top-level fields matching frontend SystemConnectionStatus interface
    assert data["backend"] == "connected"
    assert data["database"] == "connected"
    assert data["hardware"] == "disconnected"
    assert data["camera"] == "disconnected"
    assert data["aiProcessing"] == "not_initialized"
    assert "lastHeartbeatTimestamp" in data

    # Detailed subsystems dictionary verification
    subsystems = data["subsystems"]
    assert subsystems["backend"]["state"] == "connected"
    assert subsystems["database"]["state"] == "connected"
    assert subsystems["esp32_wroom"]["state"] == "disconnected"
    assert subsystems["esp32_cam"]["state"] == "disconnected"
    assert subsystems["camera"]["state"] == "disconnected"
    assert subsystems["ai_processing"]["state"] == "not_initialized"


def test_readiness_failure_when_database_unreachable():
    """Verify 503 response and not_ready status when database connection fails."""
    broken_session = MagicMock()
    broken_session.execute.side_effect = Exception("Disk I/O error or unreachable database")

    def override_broken_db():
        yield broken_session

    app.dependency_overrides[get_db] = override_broken_db
    with TestClient(app) as test_client:
        response = test_client.get("/api/v1/health/ready")
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        data = response.json()
        assert data["detail"]["status"] == "not_ready"
        assert data["detail"]["database"] is False

        # Database health check should also return 503
        db_response = test_client.get("/api/v1/health/database")
        assert db_response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        db_data = db_response.json()
        assert db_data["detail"]["status"] == "disconnected"

    app.dependency_overrides.clear()


def test_nonexistent_route_returns_404(client: TestClient):
    """Verify standard 404 response on unknown routes."""
    response = client.get("/api/v1/nonexistent-route")
    assert response.status_code == status.HTTP_404_NOT_FOUND

