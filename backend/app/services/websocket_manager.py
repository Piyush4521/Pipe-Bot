"""WebSocket Connection and Broadcast Manager.

Manages operator WebSocket connections, connection limits, initial state synchronization,
and non-blocking real-time telemetry broadcasts.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Set
from fastapi import WebSocket, status

from app.core.config import get_settings

logger = logging.getLogger("pipebot.websocket")


class WebSocketManager:
    """Manages active operator WebSocket connections and event broadcasting."""

    def __init__(self) -> None:
        self.active_connections: Set[WebSocket] = set()
        self.settings = get_settings()

    @property
    def connection_count(self) -> int:
        """Return the current number of active WebSocket connections."""
        return len(self.active_connections)

    async def connect(self, websocket: WebSocket) -> bool:
        """Accept and register a new WebSocket connection with capacity protection."""
        if len(self.active_connections) >= self.settings.WS_MAX_CONNECTIONS:
            logger.warning(
                "WebSocket connection limit (%d) reached. Rejecting incoming client.",
                self.settings.WS_MAX_CONNECTIONS,
            )
            await websocket.close(
                code=status.WS_1013_TRY_AGAIN_LATER,
                reason="Server at maximum WebSocket client capacity.",
            )
            return False

        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(
            "WebSocket client connected from %s. Active clients: %d",
            websocket.client,
            len(self.active_connections),
        )
        return True

    def disconnect(self, websocket: WebSocket) -> None:
        """Unregister a disconnected WebSocket client."""
        self.active_connections.discard(websocket)
        logger.info(
            "WebSocket client disconnected. Remaining active clients: %d",
            len(self.active_connections),
        )

    async def send_envelope(self, websocket: WebSocket, event_type: str, payload: Any) -> None:
        """Send a standardized typed envelope to an individual WebSocket client."""
        now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        envelope = {
            "type": event_type,
            "timestamp": now_utc,
            "payload": payload,
        }
        await websocket.send_json(envelope)

    async def broadcast_envelope(self, event_type: str, payload: Any) -> None:
        """Broadcast a standardized typed envelope to all connected operator clients."""
        if not self.active_connections:
            return

        now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        envelope = {
            "type": event_type,
            "timestamp": now_utc,
            "payload": payload,
        }

        dead_connections: List[WebSocket] = []
        for connection in list(self.active_connections):
            try:
                await connection.send_json(envelope)
            except Exception as exc:
                logger.warning("Failed sending message to WebSocket client %s: %s", connection.client, exc)
                dead_connections.append(connection)

        for connection in dead_connections:
            self.active_connections.discard(connection)

    async def disconnect_all(self) -> None:
        """Gracefully close all open WebSocket connections on application shutdown."""
        logger.info("Closing %d active WebSocket connections for shutdown...", len(self.active_connections))
        for connection in list(self.active_connections):
            try:
                await connection.close(
                    code=status.WS_1001_GOING_AWAY,
                    reason="Server shutting down.",
                )
            except Exception as exc:
                logger.debug("Exception closing WebSocket connection: %s", exc)
        self.active_connections.clear()


# Global WebSocket Manager Singleton
websocket_manager = WebSocketManager()

