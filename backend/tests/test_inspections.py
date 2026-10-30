"""Automated Test Suite for Inspection Sessions API and Lifecycle Rules."""

from fastapi.testclient import TestClient


def test_create_inspection_success(client: TestClient):
    """Verify inspection creation with auto-generated identifier and CREATED status."""
    payload = {
        "pipeIdentifier": "PVC-RUN-001",
        "pipeMaterial": "PVC",
        "pipeDiameterMm": 200,
        "operatorId": "TECH-001",
        "notes": "Initial calibration run",
    }
    response = client.post("/api/v1/inspections", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["id"] > 0
    assert data["inspectionId"].startswith("INSP-")
    assert data["status"] == "created"
    assert data["pipeIdentifier"] == "PVC-RUN-001"
    assert data["pipeMaterial"] == "PVC"
    assert data["pipeDiameterMm"] == 200
    assert data["operatorId"] == "TECH-001"
    assert data["startedAt"] is None
    assert data["completedAt"] is None
    assert data["totalDistanceMeters"] is None
    assert data["defectCount"] == 0
    assert "createdAt" in data
    assert "updatedAt" in data


def test_create_inspection_explicit_id(client: TestClient):
    """Verify inspection creation with an explicit custom identifier."""
    payload = {
        "inspectionId": "INSP-CUSTOM-099",
        "pipeIdentifier": "PVC-EAST-01",
        "operatorId": "TECH-002",
    }
    response = client.post("/api/v1/inspections", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["inspectionId"] == "INSP-CUSTOM-099"


def test_create_inspection_duplicate_id_conflict(client: TestClient):
    """Verify that creating an inspection with a duplicate identifier returns 409 Conflict."""
    payload = {
        "inspectionId": "INSP-DUPLICATE-001",
        "pipeIdentifier": "PVC-NORTH-01",
        "operatorId": "TECH-001",
    }
    first_resp = client.post("/api/v1/inspections", json=payload)
    assert first_resp.status_code == 201

    dup_resp = client.post("/api/v1/inspections", json=payload)
    assert dup_resp.status_code == 409
    err = dup_resp.json()
    assert err["error"] == "Conflict"


def test_create_inspection_validation_failure(client: TestClient):
    """Verify input validation rejection (missing required fields or invalid diameter)."""
    # Missing pipeIdentifier and operatorId
    bad_payload = {"pipeDiameterMm": 10}
    response = client.post("/api/v1/inspections", json=bad_payload)
    assert response.status_code == 422


def test_get_inspection_by_id_and_public_id(client: TestClient):
    """Verify retrieving an inspection by either public identifier or internal integer ID."""
    create_resp = client.post(
        "/api/v1/inspections",
        json={"pipeIdentifier": "PVC-GET-01", "operatorId": "TECH-003"},
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    pub_id = created["inspectionId"]
    internal_id = created["id"]

    # Retrieve by public string identifier
    resp_pub = client.get(f"/api/v1/inspections/{pub_id}")
    assert resp_pub.status_code == 200
    assert resp_pub.json()["inspectionId"] == pub_id

    # Retrieve by numeric integer ID
    resp_int = client.get(f"/api/v1/inspections/{internal_id}")
    assert resp_int.status_code == 200
    assert resp_int.json()["id"] == internal_id


def test_get_nonexistent_inspection_returns_404(client: TestClient):
    """Verify that fetching an unknown inspection returns 404 Not Found."""
    response = client.get("/api/v1/inspections/INSP-UNKNOWN-999")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "Not Found"


def test_list_inspections_pagination_and_ordering(client: TestClient):
    """Verify paginated listing of inspections."""
    for i in range(3):
        client.post(
            "/api/v1/inspections",
            json={"pipeIdentifier": f"PVC-PAGE-{i}", "operatorId": "TECH-PAGE"},
        )

    response = client.get("/api/v1/inspections?limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] >= 3
    assert data["limit"] == 2
    assert data["offset"] == 0


def test_list_inspections_status_filter(client: TestClient):
    """Verify listing inspections filtered by status."""
    created_resp = client.post(
        "/api/v1/inspections",
        json={"pipeIdentifier": "PVC-FILTER-01", "operatorId": "TECH-FILTER"},
    )
    insp_id = created_resp.json()["inspectionId"]

    # Start the inspection so status becomes in_progress
    client.post(f"/api/v1/inspections/{insp_id}/start")

    # Filter for in_progress
    in_prog_resp = client.get("/api/v1/inspections?status=in_progress")
    assert in_prog_resp.status_code == 200
    items = in_prog_resp.json()["items"]
    assert any(i["inspectionId"] == insp_id for i in items)
    assert all(i["status"] == "in_progress" for i in items)


def test_update_inspection_metadata(client: TestClient):
    """Verify safe updating of mutable inspection fields."""
    created_resp = client.post(
        "/api/v1/inspections",
        json={"pipeIdentifier": "PVC-ORIG-01", "operatorId": "TECH-ORIG"},
    )
    insp_id = created_resp.json()["inspectionId"]

    patch_resp = client.patch(
        f"/api/v1/inspections/{insp_id}",
        json={"pipeIdentifier": "PVC-UPDATED-01", "notes": "Sensor calibrated"},
    )
    assert patch_resp.status_code == 200
    updated = patch_resp.json()
    assert updated["pipeIdentifier"] == "PVC-UPDATED-01"
    assert updated["notes"] == "Sensor calibrated"


def test_inspection_full_lifecycle_flow(client: TestClient):
    """Verify complete inspection lifecycle: CREATED -> IN_PROGRESS -> PAUSED -> COMPLETED."""
    create_resp = client.post(
        "/api/v1/inspections",
        json={"pipeIdentifier": "PVC-LIFECYCLE-01", "operatorId": "TECH-LIFE"},
    )
    insp_id = create_resp.json()["inspectionId"]
    assert create_resp.json()["status"] == "created"

    # 1. Start inspection
    start_resp = client.post(f"/api/v1/inspections/{insp_id}/start")
    assert start_resp.status_code == 200
    start_data = start_resp.json()
    assert start_data["status"] == "in_progress"
    assert start_data["startedAt"] is not None

    # 2. Pause inspection
    pause_resp = client.post(f"/api/v1/inspections/{insp_id}/pause")
    assert pause_resp.status_code == 200
    assert pause_resp.json()["status"] == "paused"

    # 3. Complete inspection with final validated odometry distance
    complete_resp = client.post(
        f"/api/v1/inspections/{insp_id}/complete",
        json={"totalDistanceMeters": 42.18, "notes": "Inspection run completed"},
    )
    assert complete_resp.status_code == 200
    comp_data = complete_resp.json()
    assert comp_data["status"] == "completed"
    assert comp_data["completedAt"] is not None
    assert comp_data["totalDistanceMeters"] == 42.18


def test_cancel_inspection(client: TestClient):
    """Verify cancelling an inspection session."""
    create_resp = client.post(
        "/api/v1/inspections",
        json={"pipeIdentifier": "PVC-CANCEL-01", "operatorId": "TECH-CANCEL"},
    )
    insp_id = create_resp.json()["inspectionId"]

    cancel_resp = client.post(
        f"/api/v1/inspections/{insp_id}/cancel",
        json={"notes": "Obstacle blocked crawler entry"},
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"
    assert "Obstacle blocked crawler entry" in cancel_resp.json()["notes"]


def test_invalid_lifecycle_transition_returns_409(client: TestClient):
    """Verify that illegal status transitions are rejected with 409 Conflict."""
    create_resp = client.post(
        "/api/v1/inspections",
        json={"pipeIdentifier": "PVC-ILLEGAL-01", "operatorId": "TECH-ILLEGAL"},
    )
    insp_id = create_resp.json()["inspectionId"]

    # Cannot pause an inspection in CREATED status
    pause_resp = client.post(f"/api/v1/inspections/{insp_id}/pause")
    assert pause_resp.status_code == 409
    err = pause_resp.json()
    assert err["error"] == "Invalid State Transition"

    # Start the inspection
    client.post(f"/api/v1/inspections/{insp_id}/start")

    # Complete the inspection
    client.post(f"/api/v1/inspections/{insp_id}/complete")

    # Cannot start an already completed inspection
    restart_resp = client.post(f"/api/v1/inspections/{insp_id}/start")
    assert restart_resp.status_code == 409

