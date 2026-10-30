"""Custom Domain Exceptions for PipeBot Backend.

Defines standardized exceptions for domain logic, resource lookups,
and invalid state transitions.
"""

from typing import Any, Dict, Optional


class PipeBotException(Exception):
    """Base exception class for all PipeBot domain errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ResourceNotFoundError(PipeBotException):
    """Raised when a requested resource does not exist in the database."""

    def __init__(self, resource_type: str, resource_id: Any) -> None:
        message = f"{resource_type} with identifier '{resource_id}' was not found."
        super().__init__(message, {"resource_type": resource_type, "resource_id": str(resource_id)})


class ConflictError(PipeBotException):
    """Raised when an operation conflicts with existing resource state or unique constraints."""
    pass


class InvalidStateTransitionError(ConflictError):
    """Raised when an entity attempts an unauthorized or impossible status transition."""

    def __init__(self, current_status: str, target_status: str, entity_name: str = "Inspection") -> None:
        message = (
            f"Invalid state transition for {entity_name}: cannot transition from '{current_status}' to '{target_status}'."
        )
        super().__init__(
            message,
            {
                "entity": entity_name,
                "current_status": current_status,
                "target_status": target_status,
            },
        )

