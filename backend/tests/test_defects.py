"""Automated Test Suite for Defect Detections API, Filtering, and Review Status."""

from datetime import datetime, timezone
from fastapi.testclient import TestClient


def create_sample_inspection(client: TestClient) -> str:
    """Helper creating a test inspection and returning its public identifier."""
    resp = client.post(
        "/api/v1/inspections",
        json={"pipeIdentifier": "PVC-DEFECT-TEST", "operatorId": "TECH-TEST"},
    )
    assert resp.status_code == 201
    return resp.json()["inspectionId"]


def test_create_defect_success(client: TestClient):
    """Verify recording a valid defect detection linked to an inspection."""
    insp_id = create_sample_inspection(client)
    now_iso = datetime.now(timezone.utc).isoformat()

    payload = {
        "inspectionId": insp_id,
        "frameId": "FRAME-000102",
        "defectClass": "rupture",
        "confidence": 0.89,
        "boundingBox": {"x": 0.25, "y": 0.30, "width": 0.15, "height": 0.20},
        "captureTimestamp": now_iso,
        "inferenceTimestamp": now_iso,
        "estimatedDistanceMeters": 12.45,
        "notes": "Circumferential crack detected",
    }
    response = client.post("/api/v1/defects", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["id"] > 0
    assert data["defectId"].startswith("DEF-")
    assert data["defectClass"] == "Rupture"
    assert data["confidence"] == 0.89
    assert data["reviewStatus"] == "pending"
    assert data["frameId"] == "FRAME-000102"
    assert data["estimatedDistanceMeters"] == 12.45
    assert data["boundingBox"] == {"x": 0.25, "y": 0.30, "width": 0.15, "height": 0.20}
    assert "createdAt" in data
    assert "updatedAt" in data


def test_create_defect_nonexistent_inspection_returns_404(client: TestClient):
    """Verify that creating a defect for a missing inspection returns 404 Not Found."""
    payload = {
        "inspectionId": "INSP-NONEXISTENT-999",
        "frameId": "FRAME-000999",
        "defectClass": "deformation",
        "captureTimestamp": datetime.now(timezone.utc).isoformat(),
    }
    response = client.post("/api/v1/defects", json=payload)
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "Not Found"


def test_create_defect_confidence_bounds_validation(client: TestClient):
    """Verify rejection of confidence scores outside 0.0 to 1.0."""
    insp_id = create_sample_inspection(client)
    now_iso = datetime.now(timezone.utc).isoformat()

    # Confidence > 1.0
    bad_resp_high = client.post(
        "/api/v1/defects",
        json={
            "inspectionId": insp_id,
            "frameId": "FRAME-001",
            "defectClass": "obstacle",
            "confidence": 1.5,
            "captureTimestamp": now_iso,
        },
    )
    assert bad_resp_high.status_code == 422

    # Confidence < 0.0
    bad_resp_low = client.post(
        "/api/v1/defects",
        json={
            "inspectionId": insp_id,
            "frameId": "FRAME-001",
            "defectClass": "obstacle",
            "confidence": -0.1,
            "captureTimestamp": now_iso,
        },
    )
    assert bad_resp_low.status_code == 422


def test_create_defect_invalid_class_rejected(client: TestClient):
    """Verify that unsupported anomaly classes are rejected with 422."""
    insp_id = create_sample_inspection(client)
    response = client.post(
        "/api/v1/defects",
        json={
            "inspectionId": insp_id,
            "frameId": "FRAME-001",
            "defectClass": "unknown_defect_type",
            "captureTimestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert response.status_code == 422


def test_bounding_box_format_compatibility(client: TestClient):
    """Verify that frontend BoundingBox2D {xMin, yMin, xMax, yMax} format converts cleanly."""
    insp_id = create_sample_inspection(client)
    payload = {
        "inspectionId": insp_id,
        "frameId": "FRAME-CONVERT",
        "defectClass": "misalignment",
        "confidence": 0.77,
        "boundingBox": {"xMin": 100, "yMin": 150, "xMax": 250, "yMax": 300},
        "captureTimestamp": datetime.now(timezone.utc).isoformat(),
    }
    response = client.post("/api/v1/defects", json=payload)
    assert response.status_code == 201
    box = response.json()["boundingBox"]
    assert box["x"] == 100.0
    assert box["y"] == 150.0
    assert box["width"] == 150.0
    assert box["height"] == 150.0


def test_get_defect_by_id_and_public_id(client: TestClient):
    """Verify retrieving a defect record by public identifier or numeric ID."""
    insp_id = create_sample_inspection(client)
    create_resp = client.post(
        "/api/v1/defects",
        json={
            "inspectionId": insp_id,
            "frameId": "FRAME-GET-TEST",
            "defectClass": "obstacle",
            "captureTimestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    def_id = created["defectId"]
    num_id = created["id"]

    # By public defect ID
    resp_pub = client.get(f"/api/v1/defects/{def_id}")
    assert resp_pub.status_code == 200
    assert resp_pub.json()["defectId"] == def_id

    # By numeric integer ID
    resp_num = client.get(f"/api/v1/defects/{num_id}")
    assert resp_num.status_code == 200
    assert resp_num.json()["id"] == num_id


def test_get_nonexistent_defect_returns_404(client: TestClient):
    """Verify that fetching an unknown defect returns 404 Not Found."""
    response = client.get("/api/v1/defects/DEF-UNKNOWN-999")
    assert response.status_code == 404
    assert response.json()["error"] == "Not Found"


def test_list_defects_multi_criteria_filtering(client: TestClient):
    """Verify listing defects filtered by class, review status, and search query."""
    insp_id = create_sample_inspection(client)
    now_iso = datetime.now(timezone.utc).isoformat()

    # Create 3 defects
    d1 = client.post(
        "/api/v1/defects",
        json={
            "inspectionId": insp_id,
            "frameId": "FRAME-ALPHA-01",
            "defectClass": "rupture",
            "captureTimestamp": now_iso,
            "notes": "Large longitudinal fracture",
        },
    ).json()

    d2 = client.post(
        "/api/v1/defects",
        json={
            "inspectionId": insp_id,
            "frameId": "FRAME-BETA-02",
            "defectClass": "deformation",
            "captureTimestamp": now_iso,
            "notes": "Radial ovality collapse",
        },
    ).json()

    # Update d2 to confirmed
    client.patch(
        f"/api/v1/defects/{d2['defectId']}/review",
        json={"status": "confirmed", "notes": "Verified by technician"},
    )

    # 1. Filter by defect class
    resp_class = client.get("/api/v1/defects?class=rupture")
    assert resp_class.status_code == 200
    assert all(d["defectClass"] == "Rupture" for d in resp_class.json()["items"])

    # 2. Filter by review status
    resp_status = client.get("/api/v1/defects?status=confirmed")
    assert resp_status.status_code == 200
    items = resp_status.json()["items"]
    assert any(d["defectId"] == d2["defectId"] for d in items)

    # 3. Text search
    resp_search = client.get("/api/v1/defects?q=ALPHA")
    assert resp_search.status_code == 200
    search_items = resp_search.json()["items"]
    assert any(d["defectId"] == d1["defectId"] for d in search_items)


def test_update_defect_review_status(client: TestClient):
    """Verify updating operator review status and frontend alias mapping."""
    insp_id = create_sample_inspection(client)
    create_resp = client.post(
        "/api/v1/defects",
        json={
            "inspectionId": insp_id,
            "frameId": "FRAME-REVIEW",
            "defectClass": "misalignment",
            "captureTimestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
    def_id = create_resp.json()["defectId"]

    # Update using standard 'confirmed' status
    patch_resp = client.patch(
        f"/api/v1/defects/{def_id}/review",
        json={"status": "confirmed", "notes": "Joint displaced by 15mm"},
    )
    assert patch_resp.status_code == 200
    updated = patch_resp.json()
    assert updated["reviewStatus"] == "confirmed"
    assert "Joint displaced by 15mm" in updated["notes"]

    # Update using frontend alias 'dismissed' (maps to 'rejected')
    patch_alias = client.patch(
        f"/api/v1/defects/{def_id}/review",
        json={"status": "dismissed", "notes": "Shadow artifact, not misalignment"},
    )
    assert patch_alias.status_code == 200
    assert patch_alias.json()["reviewStatus"] == "rejected"


def test_soft_delete_defect(client: TestClient):
    """Verify soft-deleting defect excludes it from default listings."""
    insp_id = create_sample_inspection(client)
    create_resp = client.post(
        "/api/v1/defects",
        json={
            "inspectionId": insp_id,
            "frameId": "FRAME-DELETE-TEST",
            "defectClass": "obstacle",
            "captureTimestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
    def_id = create_resp.json()["defectId"]

    # Delete
    del_resp = client.delete(f"/api/v1/defects/{def_id}")
    assert del_resp.status_code == 200

    # Fetching deleted defect directly returns 404
    get_resp = client.get(f"/api/v1/defects/{def_id}")
    assert get_resp.status_code == 404


def test_inspection_defect_relationship_and_count(client: TestClient):
    """Verify that an inspection reflects its recorded defects and defect_count."""
    insp_id = create_sample_inspection(client)
    now_iso = datetime.now(timezone.utc).isoformat()

    # Add 2 defects
    client.post(
        "/api/v1/defects",
        json={
            "inspectionId": insp_id,
            "frameId": "F-01",
            "defectClass": "rupture",
            "captureTimestamp": now_iso,
        },
    )
    client.post(
        "/api/v1/defects",
        json={
            "inspectionId": insp_id,
            "frameId": "F-02",
            "defectClass": "obstacle",
            "captureTimestamp": now_iso,
        },
    )

    # Check inspection defect count
    insp_resp = client.get(f"/api/v1/inspections/{insp_id}")
    assert insp_resp.status_code == 200
    assert insp_resp.json()["defectCount"] == 2

    # Query defects via inspection sub-resource
    sub_resp = client.get(f"/api/v1/inspections/{insp_id}/defects")
    assert sub_resp.status_code == 200
    assert sub_resp.json()["total"] == 2
    assert len(sub_resp.json()["items"]) == 2

