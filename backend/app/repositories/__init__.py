"""Data Access Repositories Package."""

from app.repositories.inspection_repository import InspectionRepository
from app.repositories.defect_repository import DefectRepository

__all__ = ["InspectionRepository", "DefectRepository"]

