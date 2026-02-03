from __future__ import annotations

import os
import time

from azure_functions_openapi.monitoring import RequestLogger
from azure_functions_openapi.openapi import generate_openapi_spec


def _threshold(default_seconds: float, strict_seconds: float) -> float:
    return strict_seconds if os.getenv("PERF_STRICT") else default_seconds


def test_openapi_spec_generation_latency() -> None:
    # Warmup
    generate_openapi_spec()

    runs = 3
    durations: list[float] = []
    for _ in range(runs):
        start = time.perf_counter()
        generate_openapi_spec()
        durations.append(time.perf_counter() - start)

    average = sum(durations) / runs
    assert average < _threshold(5.0, 1.5)


def test_request_logging_throughput() -> None:
    iterations = 500
    logger = RequestLogger()
    start = time.perf_counter()
    for i in range(iterations):
        logger.log_request("GET", f"/perf/{i}", 200, 0.001)
    elapsed = time.perf_counter() - start

    assert elapsed < _threshold(5.0, 1.0)
