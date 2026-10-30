"""Automated Schema Migration Lifecycle and Consistency Test Suite.

Verifies end-to-end Alembic migrations exclusively against an isolated temporary
database: upgrades to head (e7f8a9b0c1d2), schema integrity, data preservation
across partial downgrade (d4d255efae0c), full downgrade to base, and re-upgrade
idempotency.
"""

from pathlib import Path
import pytest
from sqlalchemy import create_engine, text

from alembic.config import Config
from alembic import command


@pytest.fixture
def isolated_alembic_cfg(tmp_path: Path):
    """Fixture providing Alembic configuration pointed to an isolated temporary database."""
    backend_dir = Path(__file__).resolve().parent.parent
    db_file = tmp_path / "isolated_migration_val.db"
    db_url = f"sqlite:///{db_file}"

    cfg = Config(str(backend_dir / "alembic.ini"))
    cfg.set_main_option("script_location", str(backend_dir / "migrations"))
    cfg.set_main_option("sqlalchemy.url", db_url)

    yield cfg, db_url, db_file


def test_full_migration_lifecycle(isolated_alembic_cfg):
    """Test upgrade to head, partial downgrade with data preservation, full downgrade, and re-upgrade."""
    cfg, db_url, db_file = isolated_alembic_cfg

    # 1. Upgrade from empty to head (e7f8a9b0c1d2)
    command.upgrade(cfg, "head")

    engine = create_engine(db_url)
    with engine.connect() as conn:
        tables = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        ).fetchall()
        table_names = {r[0] for r in tables}

        expected_domain_tables = {
            "alembic_version",
            "inspections",
            "defects",
            "devices",
            "device_sessions",
            "device_heartbeats",
            "vehicle_status_events",
            "encoder_samples",
            "imu_samples",
            "camera_frames",
            "evidence_media",
            "ai_model_versions",
            "localization_records",
            "inspection_events",
            "inspection_summaries",
            "inspection_reports",
            "audit_events",
        }
        assert expected_domain_tables.issubset(table_names)

        # Check alembic_version contains e7f8a9b0c1d2
        ver = conn.execute(text("SELECT version_num FROM alembic_version;")).scalar_one()
        assert ver == "e7f8a9b0c1d2"

        # Seed data in inspections and defects
        conn.execute(
            text(
                "INSERT INTO inspections (inspection_id, pipe_identifier, pipe_material, "
                "pipe_diameter_mm, operator_id, status, is_archived, created_at, updated_at) "
                "VALUES ('INSP-MIG-01', 'PVC-100', 'PVC', 200, 'OP-1', 'completed', 0, "
                "'2026-10-30T12:00:00Z', '2026-10-30T12:00:00Z');"
            )
        )
        insp_id = conn.execute(
            text("SELECT id FROM inspections WHERE inspection_id='INSP-MIG-01';")
        ).scalar_one()

        conn.execute(
            text(
                "INSERT INTO defects (defect_id, inspection_id, frame_id, defect_class, "
                "confidence, capture_timestamp, review_status, is_deleted, created_at, updated_at) "
                f"VALUES ('DEF-MIG-01', {insp_id}, 'FR-01', 'Rupture', 0.95, "
                "'2026-10-30T12:05:00Z', 'confirmed', 0, '2026-10-30T12:05:00Z', '2026-10-30T12:05:00Z');"
            )
        )
        conn.commit()

    # 2. Downgrade to Stage 2 head (d4d255efae0c)
    command.downgrade(cfg, "d4d255efae0c")

    with engine.connect() as conn:
        tables = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        ).fetchall()
        table_names = {r[0] for r in tables}

        # Verify Stage 3 tables dropped
        assert "devices" not in table_names
        assert "encoder_samples" not in table_names
        assert "camera_frames" not in table_names
        assert "inspection_reports" not in table_names

        # Verify Stage 2 tables remain and data was preserved
        assert "inspections" in table_names
        assert "defects" in table_names

        insp_count = conn.execute(text("SELECT count(*) FROM inspections;")).scalar_one()
        assert insp_count == 1
        def_count = conn.execute(text("SELECT count(*) FROM defects;")).scalar_one()
        assert def_count == 1

        ver = conn.execute(text("SELECT version_num FROM alembic_version;")).scalar_one()
        assert ver == "d4d255efae0c"

        # Clear seeded records before testing full schema teardown to base
        conn.execute(text("DELETE FROM defects;"))
        conn.execute(text("DELETE FROM inspections;"))
        conn.commit()

    # 3. Full downgrade to base
    command.downgrade(cfg, "base")

    with engine.connect() as conn:
        tables = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
        ).fetchall()
        table_names = {r[0] for r in tables}
        # Inspections and defects should be gone
        assert "inspections" not in table_names
        assert "defects" not in table_names

    # 4. Re-upgrade from base to head
    command.upgrade(cfg, "head")

    with engine.connect() as conn:
        tables = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        ).fetchall()
        table_names = {r[0] for r in tables}
        assert expected_domain_tables.issubset(table_names)
        ver = conn.execute(text("SELECT version_num FROM alembic_version;")).scalar_one()
        assert ver == "e7f8a9b0c1d2"

    engine.dispose()
