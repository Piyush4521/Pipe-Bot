# PipeBot Database Performance and Latency Benchmark Report

## 1. Executive Summary and Evaluation Objectives

This benchmark report evaluates the empirical performance, transaction latency, and storage growth of the PipeBot persistence layer. All benchmarks were executed against an isolated temporary SQLite database configured with Write-Ahead Logging (WAL) and `synchronous = NORMAL`, mirroring the exact runtime parameters specified for crawler field missions.

The objective is to verify whether SQLite can sustain real-time crawler robotics requirements:
- Microcontroller telemetry streaming rate: 20Hz dual-wheel odometry and 6-axis IMU samples.
- Soft real-time latency budget: Batch insertion must execute in under 50ms to prevent network socket backpressure.
- Live dashboard retrieval: Time-slice queries must return within 20ms to ensure 60fps React rendering.

---

## 2. Test Environment and Benchmark Methodology

- Operating System: Ubuntu 22.04 LTS (WSL2 environment on Windows 11 host)
- Python Version: 3.10.12 virtual environment
- Database Engine: SQLite 3.37.2 via SQLAlchemy 2.0.44
- Database Journaling: WAL mode (`PRAGMA journal_mode = WAL`)
- Synchronous Setting: NORMAL (`PRAGMA synchronous = NORMAL`)
- Busy Timeout: 5,000 milliseconds (`PRAGMA busy_timeout = 5000`)
- Benchmark Harness: `backend/scripts/benchmark_db.py`

---

## 3. Empirical Benchmark Results

### 3.1 Telemetry Batch Ingestion Performance
Simulates 50 consecutive telemetry bursts of 20 dual-wheel rotary encoder samples (1,000 total samples) to emulate 50 seconds of continuous 20Hz robotics odometry streaming:

| Metric | Measured Value | Operational Threshold | Status |
| :--- | :--- | :--- | :--- |
| Total Samples Ingested | 1,000 samples | 1,000 | COMPLIANT |
| Batch Count | 50 batches | 50 | COMPLIANT |
| Samples per Batch | 20 samples | 20 | COMPLIANT |
| Mean Batch Latency | 0.997 ms | < 50.0 ms | EXCELLENT |
| Median Batch Latency | 0.887 ms | < 25.0 ms | EXCELLENT |
| 95th Percentile Latency (p95) | 1.612 ms | < 50.0 ms | EXCELLENT |
| 99th Percentile Latency (p99) | 1.856 ms | < 100.0 ms | EXCELLENT |
| Ingestion Throughput | 16,318.9 samples/sec | > 200 samples/sec | 81x MARGIN |

Analysis:
The measured mean batch latency of 0.997 ms is 50 times faster than the 50ms robotics deadline. The ingestion throughput of 16,318 samples/second provides enormous headroom over the physical 20Hz transmission rate.

### 3.2 Time-Series Window Query Latency
Measures the latency of querying a bounded time slice of 100 encoder samples across 100 consecutive iterations (simulating React dashboard WebSocket push and graph updates):

| Metric | Measured Value | Operational Threshold | Status |
| :--- | :--- | :--- | :--- |
| Query Iterations | 100 executions | 100 | COMPLIANT |
| Mean Query Latency | 0.942 ms | < 10.0 ms | EXCELLENT |
| 95th Percentile Latency (p95) | 1.637 ms | < 20.0 ms | EXCELLENT |

Analysis:
Sub-millisecond query retrieval enables seamless 60fps graph rendering on the React frontend without database bottlenecks or query throttling.

### 3.3 Defect Spatial Distance Ordering
Measures the performance of selecting and ordering 100 localized defect detections along the longitudinal axis of the pipeline (ordered by `estimated_distance_meters`):

| Metric | Measured Value | Operational Threshold | Status |
| :--- | :--- | :--- | :--- |
| Search Scope | 100 defect records | 100 | COMPLIANT |
| Query Iterations | 100 executions | 100 | COMPLIANT |
| Mean Query Latency | 17.169 ms | < 50.0 ms | COMPLIANT |
| 95th Percentile Latency (p95) | 34.331 ms | < 75.0 ms | COMPLIANT |

Analysis:
Spatial distance filtering and eager-loading of defect relationships executes in approximately 17ms, well within acceptable REST API response bounds (<100ms).

---

## 4. Storage Footprint and Growth Projections

| Metric | Empirical Value |
| :--- | :--- |
| Initial Schema Size | 4,096 bytes (4 KB) |
| Post-Benchmark Database Size | 430,080 bytes (~420 KB) |
| Net Growth (1,000 Samples + 100 Defects) | 425,984 bytes |
| Average Storage Footprint per Sample | 425.98 bytes |

### Projections for Extended Inspection Missions
- 10-Minute Crawler Mission (12,000 samples @ 20Hz): ~5.1 MB
- 1-Hour Comprehensive Mission (72,000 samples @ 20Hz): ~30.6 MB
- 100 Typical Missions: ~3.06 GB (excluding on-disk JPEG evidence images)

Conclusion:
SQLite file sizes remain exceptionally compact and easily fit on standard edge storage drives (e.g. 32GB to 64GB Raspberry Pi / industrial PC eMMC flash).

---

## 5. Architectural Thresholds for PostgreSQL Migration

SQLite in WAL mode is fully capable of handling local, single-crawler inspection operations. A transition to PostgreSQL 16 is recommended when any of the following architectural thresholds are reached:
1. Multi-Crawler Fleet Concurrency: When more than 5 crawlers stream telemetry concurrently to a single central backend.
2. Long-Term Multi-Territory Analytics: When historical telemetry exceeds 50 million records (>20 GB) requiring partition pruning via TimescaleDB.
3. Strict Role-Based Client Access Control: When enterprise field organizations require per-user database row-level security (RLS).

