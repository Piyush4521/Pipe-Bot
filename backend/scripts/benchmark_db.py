"""Synthetic Performance and Latency Benchmarking Script.

Executes automated write throughput, time-series query latency, and database growth
benchmarks against an isolated temporary SQLite database in WAL mode.
Never executes against or modifies production databases.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import statistics
import tempfile
import time
from typing import Any, Dict, List

from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models import (
    Defect,
    DefectClass,
    DefectReviewStatus,
    Device,
    DeviceSession,
    EncoderSample,
    IMUSample,
    Inspection,
    InspectionStatus,
)
from app.repositories import DefectRepository, InspectionRepository, TelemetryRepository


def percentile(data: List[float], p: float) -> float:
    """Calculate the p-th percentile of a sorted list of float values."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    idx = int(len(sorted_data) * (p / 100.0))
    idx = min(idx, len(sorted_data) - 1)
    return sorted_data[idx]


def run_database_benchmarks() -> Dict[str, Any]:
    """Execute isolated benchmarks and return empirical performance statistics."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "benchmark_isolated.db"
        db_url = f"sqlite:///{db_path}"

        # Initialize isolated SQLite database with WAL and foreign keys
        engine = create_engine(db_url, connect_args={"check_same_thread": False})

        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.close()

        Base.metadata.create_all(bind=engine)
        initial_file_size = db_path.stat().st_size

        session_factory = sessionmaker(bind=engine, expire_on_commit=False)
        session = session_factory()

        telem_repo = TelemetryRepository(session)
        defect_repo = DefectRepository(session)
        insp_repo = InspectionRepository(session)

        # Baseline seed
        dev = telem_repo.get_or_create_device("crawler-bench-01", "ESP32_WROOM")
        dev_sess = telem_repo.create_device_session("sess-bench-01", dev.id, "boot-01")

        insp_obj = Inspection(
            inspection_id="INSP-BENCH-01",
            pipe_identifier="PVC-BENCH-300",
            pipe_material="PVC",
            pipe_diameter_mm=300,
            operator_id="TECH-BENCH",
            status=InspectionStatus.IN_PROGRESS,
            started_at=datetime.now(timezone.utc),
        )
        insp = insp_repo.create(insp_obj)

        # Benchmark 1: Telemetry Batch Ingestion (50 batches of 20 samples = 1,000 samples)
        batch_count = 50
        batch_size = 20
        total_samples = batch_count * batch_size
        batch_insert_latencies_ms: List[float] = []

        now = datetime.now(timezone.utc)
        overall_start = time.perf_counter()

        for b in range(batch_count):
            batch = []
            for s in range(batch_size):
                idx = b * batch_size + s
                batch.append(
                    EncoderSample(
                        inspection_id=insp.id,
                        session_id=dev_sess.id,
                        sequence_number=idx + 1,
                        left_ticks=idx * 15,
                        right_ticks=idx * 15,
                        speed_mps=0.20,
                        direction="forward",
                        recorded_at=now,
                    )
                )

            t0 = time.perf_counter()
            telem_repo.insert_encoder_samples_batch(batch)
            session.commit()
            t1 = time.perf_counter()
            batch_insert_latencies_ms.append((t1 - t0) * 1000.0)

        overall_ingest_time = time.perf_counter() - overall_start
        ingest_throughput = total_samples / overall_ingest_time if overall_ingest_time > 0 else 0

        # Benchmark 2: Time-Series Range Query Latency
        query_latencies_ms: List[float] = []
        for _ in range(100):
            t0 = time.perf_counter()
            samples = telem_repo.get_encoder_samples_range(
                inspection_id=insp.id,
                start_time=now,
                end_time=datetime.now(timezone.utc),
                limit=100,
            )
            t1 = time.perf_counter()
            query_latencies_ms.append((t1 - t0) * 1000.0)

        # Benchmark 3: Spatial Defect Queries
        # Seed 100 defects
        for d in range(100):
            defect_obj = Defect(
                defect_id=f"DEF-BENCH-{d:03d}",
                inspection_id=insp.id,
                frame_id=f"FRAME-{d:03d}",
                defect_class=DefectClass.RUPTURE if d % 4 == 0 else DefectClass.DEFORMATION,
                confidence=0.85 + (d % 15) * 0.01,
                capture_timestamp=now,
                estimated_distance_meters=float(d * 0.5),
                review_status=DefectReviewStatus.CONFIRMED,
            )
            defect_repo.create(defect_obj)
        session.commit()

        defect_query_latencies_ms: List[float] = []
        for _ in range(100):
            t0 = time.perf_counter()
            defects = defect_repo.list_defects_by_distance(
                inspection_id=insp.id,
                limit=50,
            )
            t1 = time.perf_counter()
            defect_query_latencies_ms.append((t1 - t0) * 1000.0)

        session.close()
        engine.dispose()

        final_file_size = db_path.stat().st_size
        growth_bytes = final_file_size - initial_file_size

        results = {
            "environment": {
                "sqlite_version": sqlite3.sqlite_version,
                "journal_mode": "WAL",
                "synchronous": "NORMAL",
            },
            "telemetry_ingestion": {
                "total_samples": total_samples,
                "batch_count": batch_count,
                "batch_size": batch_size,
                "mean_batch_latency_ms": round(statistics.mean(batch_insert_latencies_ms), 3),
                "median_batch_latency_ms": round(statistics.median(batch_insert_latencies_ms), 3),
                "p95_batch_latency_ms": round(percentile(batch_insert_latencies_ms, 95), 3),
                "p99_batch_latency_ms": round(percentile(batch_insert_latencies_ms, 99), 3),
                "throughput_samples_per_sec": round(ingest_throughput, 1),
            },
            "telemetry_window_query": {
                "query_iterations": 100,
                "mean_query_latency_ms": round(statistics.mean(query_latencies_ms), 3),
                "p95_query_latency_ms": round(percentile(query_latencies_ms, 95), 3),
            },
            "defect_distance_query": {
                "query_iterations": 100,
                "records_searched": 100,
                "mean_query_latency_ms": round(statistics.mean(defect_query_latencies_ms), 3),
                "p95_query_latency_ms": round(percentile(defect_query_latencies_ms, 95), 3),
            },
            "storage_metrics": {
                "initial_file_bytes": initial_file_size,
                "final_file_bytes": final_file_size,
                "net_growth_bytes": growth_bytes,
                "bytes_per_sample": round(growth_bytes / total_samples, 2),
            },
        }

        return results


if __name__ == "__main__":
    benchmark_data = run_database_benchmarks()
    print(json.dumps(benchmark_data, indent=2))
