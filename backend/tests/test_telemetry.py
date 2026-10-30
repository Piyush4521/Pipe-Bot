"""Unit and Integration Tests for Telemetry Ingestion and State Management.

Verifies encoder, IMU, vehicle status, heartbeat ingestion, validation rules,
boot ID reboot tracking, sequence number monotonicity, connection health timeouts,
and optional device ingest security tokens.
"""

import time
from fastapi.testclient import TestClient
from app.core.config import get_settings
from app.services.telemetry_state import telemetry_state_service


def test_telemetry_latest_baseline_disconnected(client: TestClient) -> None:
    """Verify that initial baseline reports disconnected state with zero fabricated measurements."""
    response = client.get("/api/v1/telemetry/latest")
    assert response.status_code == 200
    data = response.json()

    assert "encoder" in data
    assert "imu" in data
    assert "vehicle" in data
    assert "timestamp" in data

    # Verify no fabricated encoder measurements
    assert data["encoder"]["leftTicks"] is None
    assert data["encoder"]["rightTicks"] is None
    assert data["encoder"]["estimatedDistanceMeters"] is None

    # Verify no fabricated IMU measurements
    assert data["imu"]["pitchDegrees"] is None
    assert data["imu"]["rollDegrees"] is None
    assert data["imu"]["accelX"] is None

    # Verify vehicle status is authentically disconnected
    assert data["vehicle"]["controllerState"] == "disconnected"
    assert data["vehicle"]["motorDriverState"] == "disconnected"
    assert data["vehicle"]["leftMotorState"] == "offline"
    assert data["vehicle"]["rightMotorState"] == "offline"


def test_telemetry_status_baseline_disconnected(client: TestClient) -> None:
    """Verify hardware connection diagnostics reports disconnected with empty device registry."""
    response = client.get("/api/v1/telemetry/status")
    assert response.status_code == 200
    data = response.json()

    assert data["overallStatus"] == "disconnected"
    assert data["devices"] == {}
    assert data["activeWsConnections"] == 0


def test_ingest_encoder_telemetry(client: TestClient) -> None:
    """Verify successful ingestion of wheel encoder odometry and reflection in latest snapshot."""
    payload = {
        "deviceId": "esp32_wroom_01",
        "bootId": "boot_session_001",
        "sequenceNumber": 1,
        "leftTicks": 1420,
        "rightTicks": 1418,
        "leftRpm": 45.2,
        "rightRpm": 45.1,
        "estimatedDistanceMeters": 3.85,
        "speedMps": 0.22,
        "direction": "forward",
    }
    response = client.post("/api/v1/telemetry/encoder", json=payload)
    assert response.status_code == 200
    res_data = response.json()

    assert res_data["leftTicks"] == 1420
    assert res_data["rightTicks"] == 1418
    assert res_data["estimatedDistanceMeters"] == 3.85
    assert res_data["direction"] == "forward"

    # Verify latest telemetry snapshot reflects this reading
    latest = client.get("/api/v1/telemetry/latest").json()
    assert latest["encoder"]["leftTicks"] == 1420
    assert latest["encoder"]["estimatedDistanceMeters"] == 3.85


def test_ingest_imu_telemetry(client: TestClient) -> None:
    """Verify successful ingestion of MPU6050 inertial measurements and angles."""
    payload = {
        "deviceId": "esp32_wroom_01",
        "bootId": "boot_session_001",
        "sequenceNumber": 2,
        "accelX": 0.05,
        "accelY": -0.02,
        "accelZ": 9.81,
        "gyroX": 0.01,
        "gyroY": -0.01,
        "gyroZ": 0.0,
        "pitchDeg": 2.4,
        "rollDeg": -1.1,
        "yawDeg": 184.5,
        "temperatureC": 34.2,
    }
    response = client.post("/api/v1/telemetry/imu", json=payload)
    assert response.status_code == 200
    res_data = response.json()

    assert res_data["pitchDegrees"] == 2.4
    assert res_data["rollDegrees"] == -1.1
    assert res_data["temperatureC"] == 34.2

    # Verify latest telemetry reflects this
    latest = client.get("/api/v1/telemetry/latest").json()
    assert latest["imu"]["pitchDegrees"] == 2.4
    assert latest["imu"]["rollDegrees"] == -1.1


def test_ingest_vehicle_status(client: TestClient) -> None:
    """Verify ingestion of read-only vehicle battery, actuation states and safety flags."""
    payload = {
        "deviceId": "esp32_wroom_01",
        "bootId": "boot_session_001",
        "sequenceNumber": 3,
        "controllerState": "connected",
        "motorDriverState": "connected",
        "leftMotorState": "forward",
        "rightMotorState": "forward",
        "emergencyStopEngaged": False,
        "commandAckState": "acknowledged",
        "batteryVoltage": 12.4,
        "batteryPercent": 88.5,
        "currentDrawAmperes": 1.25,
        "operatingState": "normal",
    }
    response = client.post("/api/v1/telemetry/vehicle/status", json=payload)
    assert response.status_code == 200
    res_data = response.json()

    assert res_data["batteryVoltage"] == 12.4
    assert res_data["batteryPercent"] == 88.5
    assert res_data["emergencyStopEngaged"] is False
    assert res_data["controllerState"] == "connected"


def test_ingest_heartbeat_updates_device_registry(client: TestClient) -> None:
    """Verify heartbeat registration and status monitoring."""
    payload = {
        "deviceId": "esp32_wroom_01",
        "deviceType": "ESP32_WROOM",
        "bootId": "boot_session_001",
        "sequenceNumber": 4,
        "uptimeSeconds": 124.5,
        "wifiRssiDbm": -58,
        "freeHeapBytes": 184320,
        "batteryVoltage": 12.35,
        "firmwareVersion": "v1.2.0",
        "status": "ok",
    }
    response = client.post("/api/v1/telemetry/heartbeat", json=payload)
    assert response.status_code == 200
    detail = response.json()

    assert detail["deviceId"] == "esp32_wroom_01"
    assert detail["connectionStatus"] == "connected"
    assert detail["uptimeSeconds"] == 124.5
    assert detail["firmwareVersion"] == "v1.2.0"

    # Status endpoint should now show the device as connected
    status_resp = client.get("/api/v1/telemetry/status").json()
    assert status_resp["overallStatus"] == "connected"
    assert "esp32_wroom_01" in status_resp["devices"]
    assert status_resp["devices"]["esp32_wroom_01"]["connectionStatus"] == "connected"


def test_reject_non_finite_float_values(client: TestClient) -> None:
    """Verify that non-finite float values (NaN, Inf) are strictly rejected with HTTP 422."""
    # Attempt to send string "NaN" which converts to float NaN
    payload = {
        "deviceId": "esp32_wroom_01",
        "bootId": "boot_session_001",
        "sequenceNumber": 5,
        "leftTicks": 100,
        "rightTicks": 100,
        "estimatedDistanceMeters": "NaN",
    }
    response = client.post("/api/v1/telemetry/encoder", json=payload)
    assert response.status_code == 422

    # Attempt to send string "Infinity"
    payload["estimatedDistanceMeters"] = "Infinity"
    response_inf = client.post("/api/v1/telemetry/encoder", json=payload)
    assert response_inf.status_code == 422


def test_sequence_number_tracking_and_duplicate_detection(client: TestClient) -> None:
    """Verify that duplicate or out-of-order sequence numbers are tracked without regressing state."""
    # 1. Send initial packet sequence 10
    client.post(
        "/api/v1/telemetry/encoder",
        json={
            "deviceId": "esp32_wroom_01",
            "bootId": "boot_session_001",
            "sequenceNumber": 10,
            "leftTicks": 500,
            "rightTicks": 500,
        },
    )

    # 2. Send duplicate packet sequence 10
    client.post(
        "/api/v1/telemetry/encoder",
        json={
            "deviceId": "esp32_wroom_01",
            "bootId": "boot_session_001",
            "sequenceNumber": 10,
            "leftTicks": 500,
            "rightTicks": 500,
        },
    )

    # 3. Send out-of-order packet sequence 8
    client.post(
        "/api/v1/telemetry/encoder",
        json={
            "deviceId": "esp32_wroom_01",
            "bootId": "boot_session_001",
            "sequenceNumber": 8,
            "leftTicks": 490,
            "rightTicks": 490,
        },
    )

    status = client.get("/api/v1/telemetry/status").json()
    dev_status = status["devices"]["esp32_wroom_01"]
    assert dev_status["lastSequenceNumber"] == 10
    assert dev_status["duplicatePacketsCount"] == 2
    assert dev_status["totalPacketsCount"] == 3


def test_device_reboot_detection(client: TestClient) -> None:
    """Verify that a changed bootId is detected as a device reboot."""
    # 1. Initial boot session
    client.post(
        "/api/v1/telemetry/heartbeat",
        json={
            "deviceId": "esp32_wroom_01",
            "deviceType": "ESP32_WROOM",
            "bootId": "boot_first_001",
            "sequenceNumber": 25,
            "uptimeSeconds": 1500.0,
        },
    )

    # 2. Device reboots with new bootId and reset sequence number
    client.post(
        "/api/v1/telemetry/heartbeat",
        json={
            "deviceId": "esp32_wroom_01",
            "deviceType": "ESP32_WROOM",
            "bootId": "boot_second_002",
            "sequenceNumber": 1,
            "uptimeSeconds": 2.0,
        },
    )

    status = client.get("/api/v1/telemetry/status").json()
    dev_status = status["devices"]["esp32_wroom_01"]
    assert dev_status["bootId"] == "boot_second_002"
    assert dev_status["rebootCount"] == 1
    assert dev_status["lastSequenceNumber"] == 1


def test_stale_and_disconnected_timeout_evaluation(client: TestClient) -> None:
    """Verify that elapsed time correctly transitions device states from connected to stale to disconnected."""
    # 1. Send heartbeat
    client.post(
        "/api/v1/telemetry/heartbeat",
        json={
            "deviceId": "esp32_wroom_01",
            "deviceType": "ESP32_WROOM",
            "bootId": "boot_session_001",
            "sequenceNumber": 1,
        },
    )

    record = telemetry_state_service._devices["esp32_wroom_01"]

    # Initial state is connected
    assert telemetry_state_service.get_device_status("esp32_wroom_01").value == "connected"

    # Simulate 3.5 seconds elapsed (past TELEMETRY_STALE_TIMEOUT_SECONDS = 3.0s, before HEARTBEAT_TIMEOUT_SECONDS = 5.0s)
    record.last_seen_monotonic = time.monotonic() - 3.5
    assert telemetry_state_service.get_device_status("esp32_wroom_01").value == "stale"

    # Simulate 6.0 seconds elapsed (past HEARTBEAT_TIMEOUT_SECONDS = 5.0s)
    record.last_seen_monotonic = time.monotonic() - 6.0
    assert telemetry_state_service.get_device_status("esp32_wroom_01").value == "disconnected"


def test_device_ingest_token_authentication(client: TestClient, monkeypatch) -> None:
    """Verify token authentication when DEVICE_INGEST_TOKEN is configured."""
    settings = get_settings()
    monkeypatch.setattr(settings, "DEVICE_INGEST_TOKEN", "secret-hardware-token-12345")

    payload = {
        "deviceId": "esp32_wroom_01",
        "bootId": "boot_session_001",
        "sequenceNumber": 1,
        "leftTicks": 100,
        "rightTicks": 100,
    }

    # 1. Request without token is rejected with HTTP 401
    resp_no_token = client.post("/api/v1/telemetry/encoder", json=payload)
    assert resp_no_token.status_code == 401
    assert "Invalid or missing device ingestion token" in resp_no_token.json()["detail"]

    # 2. Request with invalid token is rejected with HTTP 401
    resp_bad_token = client.post(
        "/api/v1/telemetry/encoder",
        json=payload,
        headers={"X-Device-Token": "wrong-token"},
    )
    assert resp_bad_token.status_code == 401

    # 3. Request with valid X-Device-Token succeeds
    resp_valid_header = client.post(
        "/api/v1/telemetry/encoder",
        json=payload,
        headers={"X-Device-Token": "secret-hardware-token-12345"},
    )
    assert resp_valid_header.status_code == 200

    # 4. Request with valid Authorization: Bearer token succeeds
    resp_valid_bearer = client.post(
        "/api/v1/telemetry/encoder",
        json=payload,
        headers={"Authorization": "Bearer secret-hardware-token-12345"},
    )
    assert resp_valid_bearer.status_code == 200


def test_inspection_telemetry_log_endpoint(client: TestClient) -> None:
    """Verify that telemetry log query for an inspection returns valid response."""
    response = client.get("/api/v1/telemetry/inspection/INSP-2026-TEST")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "encoder" in data[0]
