"""PipeBot FastAPI Application Entry Point.

Configures FastAPI instance, CORS middleware, centralized exception handling,
lifespan events, and API version 1 routing.
"""

import logging
from typing import Any, Dict

from fastapi import FastAPI, Request, WebSocket, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.endpoints.websocket import websocket_telemetry_stream
from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.exceptions import (
    ConflictError,
    InvalidStateTransitionError,
    PipeBotException,
    ResourceNotFoundError,
)
from app.core.lifespan import lifespan

logger = logging.getLogger("pipebot.main")
settings = get_settings()


def create_application() -> FastAPI:
    """Application factory building and configuring the FastAPI instance."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "PipeBot AI-powered robotic pipeline inspection backend service. "
            "Provides hardware diagnostics, mission tracking, and computer vision integration."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # 1. Configure CORS Middleware
    origins = settings.cors_origins_list
    logger.info("Configuring CORS middleware with allowed origins: %s", origins)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # 2. Centralized Exception Handlers
    @app.exception_handler(ResourceNotFoundError)
    async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError) -> JSONResponse:
        """Handle missing resource exceptions with HTTP 404."""
        logger.info("Resource not found on %s: %s", request.url.path, exc.message)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "Not Found",
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(InvalidStateTransitionError)
    async def state_transition_handler(request: Request, exc: InvalidStateTransitionError) -> JSONResponse:
        """Handle invalid state transitions with HTTP 409 Conflict."""
        logger.warning("Invalid state transition on %s: %s", request.url.path, exc.message)
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "Invalid State Transition",
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
        """Handle resource conflicts or unique constraint violations with HTTP 409."""
        logger.warning("Conflict error on %s: %s", request.url.path, exc.message)
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "Conflict",
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(PipeBotException)
    async def pipebot_domain_exception_handler(request: Request, exc: PipeBotException) -> JSONResponse:
        """Handle generic PipeBot domain exceptions with HTTP 400."""
        logger.warning("Domain exception on %s: %s", request.url.path, exc.message)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Bad Request",
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle request validation errors with sanitized field messages."""
        logger.warning("Request validation failed on %s: %s", request.url.path, exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "message": "Input validation failed for request payload or parameters.",
                "details": jsonable_encoder(exc.errors()),
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions without leaking server stack traces to clients."""
        logger.error("Unhandled server exception on %s: %s", request.url.path, exc, exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected server error occurred. Please consult backend logs.",
            },
        )

    # 3. Root Endpoint
    @app.get(
        "/",
        tags=["General"],
        summary="Application Root Identity",
        description="Returns application name, version, documentation URL, and running status.",
    )
    def root() -> Dict[str, Any]:
        """Simple application identity response."""
        return {
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "environment": settings.APP_ENV,
            "docs_url": "/docs",
            "api_prefix": settings.API_V1_PREFIX,
        }

    # 4. Include Versioned API Routers
    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

    # 5. Root-level WebSocket Compatibility Aliases
    @app.websocket("/ws/telemetry")
    @app.websocket("/ws")
    async def root_websocket_telemetry_alias(websocket: WebSocket) -> None:
        """Compatibility WebSocket route matching frontend configuration."""
        await websocket_telemetry_stream(websocket)

    # 6. Frontend Contract Compatibility Aliases
    from app.api.v1.endpoints.health import get_health
    from app.api.v1.endpoints.system import get_system_status

    @app.get("/status", tags=["Compatibility Aliases"], include_in_schema=False)
    @app.get("/api/v1/status", tags=["Compatibility Aliases"], include_in_schema=False)
    def status_alias():
        """Frontend compatibility alias for system status contract."""
        return get_system_status()

    @app.get("/health", tags=["Compatibility Aliases"], include_in_schema=False)
    def health_alias():
        """Frontend compatibility alias for health check."""
        return get_health()

    return app


app = create_application()

