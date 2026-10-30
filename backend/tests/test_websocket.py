"""Unit and Integration Tests for WebSocket Communication and Broadcasts.

Verifies operator WebSocket connections, route compatibility aliases (/api/v1/ws/telemetry,
/ws/telemetry, /ws), initial state snapshot delivery, ping/pong keepalives,
real-time telemetry broadcasting, and capacity limit enforcement.
"""

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.core.config import get_settings
from app.services.websocket_manager import websocket_manager


def test_websocket_connection_and_initial_snapshots(client: TestClient) -> None:
    """Verify WebSocket connection delivers four initial state envelopes immediately upon connect."""
    with client.websocket_connect("/api/v1/ws/telemetry") as ws:
        # Envelope 1: system_status
        msg1 = ws.receive_json()
        assert msg1["type"] == "system_status"
        assert "timestamp" in msg1
        assert "backend" in msg1["payload"]

        # Envelope 2: telemetry_encoder
        msg2 = ws.receive_json()
        assert msg2["type"] == "telemetry_encoder"
        assert "leftTicks" in msg2["payload"]

        # Envelope 3: telemetry_imu
        msg3 = ws.receive_json()
        assert msg3["type"] == "telemetry_imu"
        assert "pitchDegrees" in msg3["payload"]

        # Envelope 4: vehicle_status
        msg4 = ws.receive_json()
        assert msg4["type"] == "vehicle_status"
        assert "controllerState" in msg4["payload"]


def test_websocket_route_compatibility_aliases(client: TestClient) -> None:
    """Verify that /ws/telemetry and /ws route aliases function identically to /api/v1/ws/telemetry."""
    # Test alias 1: /ws/telemetry
    with client.websocket_connect("/ws/telemetry") as ws1:
        msg = ws1.receive_json()
        assert msg["type"] == "system_status"

    # Test alias 2: /ws
    with client.websocket_connect("/ws") as ws2:
        msg = ws2.receive_json()
        assert msg["type"] == "system_status"


def test_websocket_ping_pong_keepalive(client: TestClient) -> None:
    """Verify that client ping message receives an active pong envelope response."""
    with client.websocket_connect("/api/v1/ws/telemetry") as ws:
        # Drain initial 4 envelopes
        for _ in range(4):
            ws.receive_json()

        # Send ping
        ws.send_json({"type": "ping"})
        response = ws.receive_json()

        assert response["type"] == "pong"
        assert response["payload"]["status"] == "active"
        assert "timestamp" in response["payload"]


def test_websocket_broadcast_on_telemetry_ingestion(client: TestClient) -> None:
    """Verify that ingesting telemetry triggers real-time broadcast to connected WebSocket clients."""
    with client.websocket_connect("/api/v1/ws/telemetry") as ws:
        # Drain initial snapshots
        for _ in range(4):
            ws.receive_json()

        # Ingest new encoder telemetry via REST API
        ingest_payload = {
            "deviceId": "esp32_wroom_01",
            "bootId": "boot_session_001",
            "sequenceNumber": 50,
            "leftTicks": 2500,
            "rightTicks": 2498,
            "leftRpm": 40.0,
            "rightRpm": 40.0,
            "estimatedDistanceMeters": 6.72,
            "speedMps": 0.25,
            "direction": "forward",
        }
        res = client.post("/api/v1/telemetry/encoder", json=ingest_payload)
        assert res.status_code == 200

        # Connected WebSocket client must receive the broadcast envelope
        broadcast_msg = ws.receive_json()
        assert broadcast_msg["type"] == "telemetry_encoder"
        assert broadcast_msg["payload"]["leftTicks"] == 2500
        assert broadcast_msg["payload"]["estimatedDistanceMeters"] == 6.72


def test_websocket_capacity_limit_enforcement(client: TestClient, monkeypatch) -> None:
    """Verify that incoming WebSocket connections exceeding WS_MAX_CONNECTIONS are rejected."""
    settings = get_settings()
    monkeypatch.setattr(settings, "WS_MAX_CONNECTIONS", 2)
    monkeypatch.setattr(websocket_manager.settings, "WS_MAX_CONNECTIONS", 2)

    with client.websocket_connect("/api/v1/ws/telemetry") as ws1:
        with client.websocket_connect("/api/v1/ws/telemetry") as ws2:
            assert websocket_manager.connection_count == 2

            # Third connection attempt should be rejected
            with pytest.raises(WebSocketDisconnect) as exc_info:
                with client.websocket_connect("/api/v1/ws/telemetry") as _:
                    pass
            assert exc_info.value.code == 1013


def test_websocket_disconnect_cleanup(client: TestClient) -> None:
    """Verify that when a client closes, active connection count accurately decrements."""
    initial_count = websocket_manager.connection_count
    with client.websocket_connect("/api/v1/ws/telemetry") as _:
        assert websocket_manager.connection_count == initial_count + 1

    assert websocket_manager.connection_count == initial_count

