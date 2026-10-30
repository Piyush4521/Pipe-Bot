"""Automated Test Suite for Database Integrity, Restrictive Foreign Keys, and Archival."""

from datetime import datetime, timezone
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.core.exceptions import ConflictError
from app.models.defect import Defect, DefectClass, DefectReviewStatus
from app.models.inspection import Inspection, InspectionStatus
from app.services.inspection_service import InspectionService


def test_restrictive_foreign_key_prevents_destructive_deletion(db_session: Session):
    """Verify that restrictive foreign keys prevent deleting an inspection with associated defects.

    Under the audit-preservation policy, attempting to execute raw SQL deletion on a parent
    inspection must raise IntegrityError because defects exist.
    """
    # 1. Create an inspection
    inspection = Inspection(
        inspection_id="INSP-RESTRICT-001",
        pipe_identifier="PVC-RESTRICT",
        operator_id="TECH-RESTRICT",
        status=InspectionStatus.CREATED,
    )
    db_session.add(inspection)
    db_session.commit()
    db_session.refresh(inspection)

    # 2. Add an associated defect
    defect = Defect(
        defect_id="DEF-RESTRICT-001",
        inspection_id=inspection.id,
        frame_id="FRAME-RESTRICT",
        defect_class=DefectClass.RUPTURE,
        capture_timestamp=datetime.now(timezone.utc),
        review_status=DefectReviewStatus.PENDING,
    )
    db_session.add(defect)
    db_session.commit()
    db_session.refresh(defect)

    # 3. Attempting to delete inspection must fail under RESTRICT policy
    db_session.delete(inspection)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # 4. Verify both inspection and defect remain completely intact
    remaining_defect = db_session.execute(
        select(Defect).where(Defect.defect_id == "DEF-RESTRICT-001")
    ).scalar_one_or_none()
    assert remaining_defect is not None
    assert remaining_defect.defect_id == "DEF-RESTRICT-001"

    remaining_inspection = db_session.execute(
        select(Inspection).where(Inspection.inspection_id == "INSP-RESTRICT-001")
    ).scalar_one_or_none()
    assert remaining_inspection is not None


def test_service_level_permanent_deletion_strictly_prohibited(db_session: Session):
    """Verify that service layer rejects permanent inspection deletion."""
    service = InspectionService(db_session)
    insp = Inspection(
        inspection_id="INSP-NODELETE-001",
        pipe_identifier="PVC-ND",
        operator_id="TECH-ND",
        status=InspectionStatus.CREATED,
    )
    db_session.add(insp)
    db_session.commit()

    with pytest.raises(ConflictError) as exc_info:
        service.delete_inspection("INSP-NODELETE-001")
    assert "strictly forbidden" in str(exc_info.value.message)


def test_defect_evidence_survives_inspection_archival(db_session: Session):
    """Verify that archiving an inspection preserves all defect records intact."""
    service = InspectionService(db_session)
    inspection = Inspection(
        inspection_id="INSP-ARCHIVE-001",
        pipe_identifier="PVC-ARCH-01",
        operator_id="TECH-ARCH",
        status=InspectionStatus.CREATED,
        is_archived=False,
    )
    db_session.add(inspection)
    db_session.commit()
    db_session.refresh(inspection)

    defect = Defect(
        defect_id="DEF-ARCHIVE-001",
        inspection_id=inspection.id,
        frame_id="FRAME-ARCH-01",
        defect_class=DefectClass.DEFORMATION,
        capture_timestamp=datetime.now(timezone.utc),
    )
    db_session.add(defect)
    db_session.commit()

    # Archive inspection via service
    archived = service.archive_inspection(inspection.inspection_id)
    assert archived.is_archived is True

    # Confirm defect evidence is preserved and still links to the archived inspection
    defects, total = service.get_inspection_defects(inspection.inspection_id)
    assert total == 1
    assert defects[0].defect_id == "DEF-ARCHIVE-001"
    assert defects[0].is_deleted is False


def test_archived_inspections_remain_retrievable_via_api(client: TestClient):
    """Verify that archived inspections can still be retrieved for historical audits."""
    create_resp = client.post(
        "/api/v1/inspections",
        json={"pipeIdentifier": "PVC-ARCH-API", "operatorId": "TECH-ARCH-API"},
    )
    insp_id = create_resp.json()["inspectionId"]

    # Add a defect
    client.post(
        "/api/v1/defects",
        json={
            "inspectionId": insp_id,
            "frameId": "FRAME-ARCH-API",
            "defectClass": "obstacle",
            "captureTimestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

    # Archive the inspection via API
    arch_resp = client.post(f"/api/v1/inspections/{insp_id}/archive")
    assert arch_resp.status_code == 200
    assert arch_resp.json()["isArchived"] is True

    # 1. Fetching single inspection directly by ID succeeds
    get_resp = client.get(f"/api/v1/inspections/{insp_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["isArchived"] is True

    # 2. Defect list under archived inspection is still fully accessible
    def_resp = client.get(f"/api/v1/inspections/{insp_id}/defects")
    assert def_resp.status_code == 200
    assert def_resp.json()["total"] == 1

    # 3. Listing inspections with include_archived=false excludes it
    list_active = client.get("/api/v1/inspections?include_archived=false")
    assert not any(i["inspectionId"] == insp_id for i in list_active.json()["items"])

    # 4. Listing inspections with include_archived=true includes it
    list_all = client.get("/api/v1/inspections?include_archived=true")
    assert any(i["inspectionId"] == insp_id for i in list_all.json()["items"])


def test_api_rejects_permanent_inspection_deletion(client: TestClient):
    """Verify that calling DELETE on an inspection returns 409 Conflict."""
    create_resp = client.post(
        "/api/v1/inspections",
        json={"pipeIdentifier": "PVC-DEL-REJECT", "operatorId": "TECH-DEL"},
    )
    insp_id = create_resp.json()["inspectionId"]

    del_resp = client.delete(f"/api/v1/inspections/{insp_id}")
    assert del_resp.status_code == 409
    assert "strictly forbidden" in del_resp.json()["message"]


def test_unique_inspection_id_constraint(db_session: Session):
    """Verify database-level unique constraint on inspection_id."""
    insp1 = Inspection(
        inspection_id="INSP-UNIQUE-999",
        pipe_identifier="PVC-U1",
        operator_id="TECH-U1",
        status=InspectionStatus.CREATED,
    )
    db_session.add(insp1)
    db_session.commit()

    insp2 = Inspection(
        inspection_id="INSP-UNIQUE-999",
        pipe_identifier="PVC-U2",
        operator_id="TECH-U2",
        status=InspectionStatus.CREATED,
    )
    db_session.add(insp2)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_unique_defect_id_constraint(db_session: Session):
    """Verify database-level unique constraint on defect_id."""
    inspection = Inspection(
        inspection_id="INSP-DEF-UNIQ",
        pipe_identifier="PVC-DU",
        operator_id="TECH-DU",
        status=InspectionStatus.CREATED,
    )
    db_session.add(inspection)
    db_session.commit()

    d1 = Defect(
        defect_id="DEF-DUPLICATE-ID",
        inspection_id=inspection.id,
        frame_id="FRAME-1",
        defect_class=DefectClass.OBSTACLE,
        capture_timestamp=datetime.now(timezone.utc),
    )
    db_session.add(d1)
    db_session.commit()

    d2 = Defect(
        defect_id="DEF-DUPLICATE-ID",
        inspection_id=inspection.id,
        frame_id="FRAME-2",
        defect_class=DefectClass.MISALIGNMENT,
        capture_timestamp=datetime.now(timezone.utc),
    )
    db_session.add(d2)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_transaction_rollback_preserves_state(db_session: Session):
    """Verify that an aborted transaction rolls back without leaving partial writes."""
    initial_count = db_session.query(Inspection).count()

    try:
        insp = Inspection(
            inspection_id="INSP-ROLLBACK-TEST",
            pipe_identifier="PVC-RB",
            operator_id="TECH-RB",
            status=InspectionStatus.CREATED,
        )
        db_session.add(insp)
        db_session.flush()

        raise RuntimeError("Simulated transaction fault")
    except RuntimeError:
        db_session.rollback()

    final_count = db_session.query(Inspection).count()
    assert final_count == initial_count
