"""Measured, non-promotional cross-language benchmark runner."""
from __future__ import annotations

import json
import statistics
import subprocess
import time
from pathlib import Path
from typing import Any, Iterable

from .build import build_floor
from .registry import REPO_ROOT, TowerRegistry


def _measure(argv: list[str], iterations: int) -> dict[str, Any]:
    if iterations < 1:
        return {
            "status": "INVALID_BENCHMARK",
            "argv": argv,
            "error": "iterations must be at least 1",
        }
    samples: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        try:
            completed = subprocess.run(
                argv,
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                timeout=120,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return {
                "status": "FAILED_TIMEOUT",
                "argv": argv,
                "returncode": None,
                "stderr": (exc.stderr or "")[-2000:] if isinstance(exc.stderr, str) else "",
            }
        except OSError as exc:
            return {
                "status": "BLOCKED_TOOLCHAIN",
                "argv": argv,
                "returncode": None,
                "stderr": str(exc),
            }
        elapsed = (time.perf_counter() - start) * 1000
        if completed.returncode != 0:
            return {
                "status": "FAILED",
                "argv": argv,
                "returncode": completed.returncode,
                "stderr": completed.stderr[-2000:],
            }
        samples.append(elapsed)
    return {
        "status": "MEASURED",
        "argv": argv,
        "iterations": iterations,
        "median_ms": round(statistics.median(samples), 3),
        "min_ms": round(min(samples), 3),
        "max_ms": round(max(samples), 3),
        "samples_ms": [round(value, 3) for value in samples],
    }


def benchmark_many(
    registry: TowerRegistry,
    technology_ids: Iterable[str],
    *,
    iterations: int = 3,
) -> dict[str, Any]:
    requested_list = list(technology_ids)
    if not requested_list or (len(requested_list) == 1 and requested_list[0].casefold() == "all"):
        requested_list = [tech["id"] for tech in registry.technologies]
    requested = {value.casefold() for value in requested_list}
    known = {
        tech.get("id", "").casefold(): tech
        for tech in registry.technologies
        if isinstance(tech, dict) and isinstance(tech.get("id"), str)
    }
    results: list[dict[str, Any]] = []
    for normalized_id in sorted(requested):
        tech = known.get(normalized_id)
        if tech is None:
            original = next(value for value in requested_list if value.casefold() == normalized_id)
            results.append({
                "technology_id": original,
                "status": "INVALID_MANIFEST",
                "build_status": "INVALID_MANIFEST",
                "blocker": f"Unknown technology requested: {original}",
            })
            continue
        build = build_floor(tech)
        row: dict[str, Any] = {
            "technology_id": tech["id"],
            "build_status": build["status"],
            "evidence_state": tech["evidence_state"],
            "proof_class": tech["proof_class"],
        }
        if build["status"] != "VERIFIED":
            row["status"] = build["status"]
            row["blocker"] = build.get("blocker", "")
        else:
            tests = tech["toolchain"].get("test", [])
            if not tests:
                row["status"] = "NO_RUNTIME_BENCHMARK"
            elif iterations < 1:
                row["status"] = "INVALID_BENCHMARK"
                row["blocker"] = "iterations must be at least 1"
            else:
                row["measurement"] = _measure(tests[-1], iterations)
                row["status"] = row["measurement"]["status"]
        results.append(row)
    return {
        "benchmark_id": "tower-portable-benchmark-v1",
        "iterations": iterations,
        "requested_technology_ids": requested_list,
        "results": results,
        "truth_note": "Measurements are local process timings for the declared exhibit commands, not universal language rankings.",
    }


def write_benchmark(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
