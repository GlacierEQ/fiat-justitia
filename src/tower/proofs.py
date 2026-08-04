"""Build-bound proof and evidence report."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .registry import TowerRegistry


def _build_statuses(build_report: dict[str, Any]) -> dict[str, str]:
    """Return one status per technology and reject ambiguous duplicate rows."""
    statuses: dict[str, str] = {}
    rows = build_report.get("results", [])
    if not isinstance(rows, list):
        raise ValueError("build report results must be a list")
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"build report result {index} must be an object")
        technology_id = row.get("technology_id")
        status = row.get("status")
        if not isinstance(technology_id, str) or not technology_id:
            raise ValueError(f"build report result {index} requires technology_id")
        if not isinstance(status, str) or not status:
            raise ValueError(f"build report result {technology_id} requires status")
        if technology_id in statuses:
            raise ValueError(f"duplicate build result for technology: {technology_id}")
        statuses[technology_id] = status
    return statuses


def _benchmark_statuses(benchmark_report: dict[str, Any] | None) -> dict[str, str]:
    statuses: dict[str, str] = {}
    if benchmark_report is None:
        return statuses
    rows = benchmark_report.get("results", [])
    if not isinstance(rows, list):
        raise ValueError("benchmark report results must be a list")
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"benchmark report result {index} must be an object")
        technology_id = row.get("technology_id")
        status = row.get("status")
        if not isinstance(technology_id, str) or not technology_id:
            raise ValueError(f"benchmark report result {index} requires technology_id")
        if not isinstance(status, str) or not status:
            raise ValueError(f"benchmark report result {technology_id} requires status")
        if technology_id in statuses:
            raise ValueError(f"duplicate benchmark result for technology: {technology_id}")
        statuses[technology_id] = status
    return statuses


def _benchmark_proof_status(status: str) -> str:
    if status == "MEASURED":
        return "SATISFIED_FOR_DECLARED_GATE"
    if status.startswith("BLOCKED_"):
        return "BLOCKED"
    if status in {"NOT_EXECUTED", "NO_RUNTIME_BENCHMARK"}:
        return "NOT_EXECUTED"
    return "FAILED"


def build_proof_report(
    registry: TowerRegistry,
    build_report: dict[str, Any],
    benchmark_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Bind each governed floor's proof state to its unique executed evidence."""
    statuses = _build_statuses(build_report)
    benchmarks = _benchmark_statuses(benchmark_report)
    governed_ids = {technology["id"] for technology in registry.technologies}
    unknown_ids = sorted((set(statuses) | set(benchmarks)) - governed_ids)
    if unknown_ids:
        raise ValueError(f"evidence report contains unknown technologies: {', '.join(unknown_ids)}")

    floors = []
    for tech in registry.technologies:
        tech_id = tech["id"]
        build_status = statuses.get(tech_id, "NOT_EXECUTED")
        benchmark_status = benchmarks.get(tech_id, "NOT_EXECUTED")
        proof_class = tech["proof_class"]
        if build_status.startswith("BLOCKED_"):
            proof_status = "BLOCKED"
        elif build_status == "NOT_EXECUTED":
            proof_status = "NOT_EXECUTED"
        elif build_status != "VERIFIED":
            proof_status = "FAILED"
        elif proof_class == "benchmark":
            proof_status = _benchmark_proof_status(benchmark_status)
        else:
            proof_status = "SATISFIED_FOR_DECLARED_GATE"
        floors.append({
            "technology_id": tech_id,
            "easy_example": tech["easy_example"],
            "advanced_example": tech["advanced_example"],
            "evidence_state": tech["evidence_state"],
            "proof_class": proof_class,
            "build_status": build_status,
            "benchmark_status": benchmark_status,
            "proof_status": proof_status,
            "primary_evidence": tech["primary_evidence"],
        })
    return {
        "proof_report_id": "tower-proof-report-v1",
        "tower_id": registry.payload["tower_id"],
        "floors": floors,
        "counts": {
            status: sum(1 for floor in floors if floor["proof_status"] == status)
            for status in sorted({floor["proof_status"] for floor in floors})
        },
    }


def write_proof_report(report: dict[str, Any], path: Path) -> None:
    """Persist a deterministic, human-readable proof report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
