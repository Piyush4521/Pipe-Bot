"""Automated Performance and Latency Benchmark Validation Test.

Validates that batch insertion and query latencies meet soft real-time robotics
thresholds in an isolated temporary test database.
"""

from scripts.benchmark_db import run_database_benchmarks


def test_database_performance_benchmarks():
    """Verify that empirical benchmark results meet operational latency thresholds."""
    results = run_database_benchmarks()

    # Telemetry ingestion assertions
    telem = results["telemetry_ingestion"]
    assert telem["total_samples"] == 1000
    assert telem["mean_batch_latency_ms"] < 50.0  # Mean batch latency well under 50ms
    assert telem["throughput_samples_per_sec"] > 200.0  # Throughput exceeds 200 samples/sec

    # Query latency assertions
    window_q = results["telemetry_window_query"]
    assert window_q["mean_query_latency_ms"] < 20.0  # Window queries under 20ms

    defect_q = results["defect_distance_query"]
    assert defect_q["mean_query_latency_ms"] < 50.0  # Defect spatial queries under 50ms

    # Storage assertions
    storage = results["storage_metrics"]
    assert storage["final_file_bytes"] > storage["initial_file_bytes"]
    assert storage["bytes_per_sample"] < 1000  # Compact footprint per record
