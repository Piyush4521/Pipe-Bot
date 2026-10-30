"""WebSocket Telemetry Server Endpoint.

Provides duplex real-time streaming of telemetry events, vehicle status,
and system link health to operator dashboard clients.
"""

from datetime import datetime, timezone
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.db.session import SessionLocal
from app.services.health_service import HealthService
from app.services.telemetry_state import telemetry_state_service
from app.services.websocket_manager import websocket_manager

logger = logging.getLogger("pipebot.websocket_endpoint")
router = APIRouter(tags=["WebSocket Stream"])


@router.websocket("/ws/telemetry")
async def websocket_telemetry_stream(websocket: WebSocket) -> None:
    """Duplex WebSocket endpoint for real-time telemetry streaming and operator updates."""
    is_accepted = await websocket_manager.connect(websocket)
    if not is_accepted:
        return

    # 1. Send initial state snapshot on connection
    try:
        db = SessionLocal()
        try:
            sys_status = HealthService.get_system_status(db)
            await websocket_manager.send_envelope(
                websocket=websocket,
                event_type="system_status",
                payload=sys_status.model_dump(by_alias=True),
            )
        finally:
            db.close()

        # Send latest sensor states if available
        latest = telemetry_state_service.get_latest_telemetry()
        await websocket_manager.send_envelope(
            websocket=websocket,
            event_type="telemetry_encoder",
            payload=latest.encoder.model_dump(by_alias=True),
        )
        await websocket_manager.send_envelope(
            websocket=websocket,
            event_type="telemetry_imu",
            payload=latest.imu.model_dump(by_alias=True),
        )
        await websocket_manager.send_envelope(
            websocket=websocket,
            event_type="vehicle_status",
            payload=latest.vehicle.model_dump(by_alias=True),
        )
    except Exception as exc:
        logger.warning("Error dispatching initial state snapshot to WebSocket: %s", exc)

    # 2. Maintain connection and handle incoming client messages (heartbeat/ping)
    try:
        while True:
            text_data = await websocket.receive_text()
            try:
                message = json.loads(text_data)
                msg_type = message.get("type", "")

                if msg_type == "ping":
                    now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                    await websocket_manager.send_envelope(
                        websocket=websocket,
                        event_type="pong",
                        payload={"timestamp": now_utc, "status": "active"},
                    )
                elif msg_type == "request_snapshot":
                    current_snap = telemetry_state_service.get_latest_telemetry()
                    await websocket_manager.send_envelope(
                        websocket=websocket,
                        event_type="telemetry_snapshot",
                        payload=current_snap.model_dump(by_alias=True),
                    )
            except json.JSONDecodeError:
                logger.debug("Received non-JSON message from WebSocket client: %s", text_data)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as exc:
        logger.debug("WebSocket client disconnected with exception: %s", exc)
        websocket_manager.disconnect(websocket)

