#!/usr/bin/env python3
"""Persist and verify the flagship mission chain through the governed SQL schema."""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def read_object(path: Path, label: str) -> dict:
    """Read one required JSON object from disk."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a JSON object")
    return payload


def require_string(payload: dict, field: str, label: str) -> str:
    """Return one non-empty string field or fail with a precise contract error."""
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}.{field} must be a non-empty string")
    return value


def require_sha256(payload: dict, field: str, label: str) -> str:
    value = require_string(payload, field, label)
    if not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{label}.{field} must be a lowercase SHA-256 digest")
    return value


def main() -> int:
    """Apply the schema, persist the chain, and prove it by readback."""
    if len(sys.argv) != 8:
        raise SystemExit(
            "usage: persist_state <schema.sql> <db> <mission.json> <decision.json> "
            "<event.json> <plan.json> <readback.json>"
        )
    schema_path, db_path, mission_path, decision_path, event_path, plan_path, output_path = map(
        Path, sys.argv[1:]
    )
    mission = read_object(mission_path, "mission")
    decision = read_object(decision_path, "decision")
    event = read_object(event_path, "event")
    plan = read_object(plan_path, "plan")

    mission_id = require_string(mission, "mission_id", "mission")
    if require_string(decision, "mission_id", "decision") != mission_id:
        raise ValueError("decision mission_id does not match mission")
    if require_string(event, "mission_id", "event") != mission_id:
        raise ValueError("event mission_id does not match mission")
    if require_string(plan, "mission_id", "plan") != mission_id:
        raise ValueError("plan mission_id does not match mission")

    input_sha256 = require_sha256(mission, "input_sha256", "mission")
    if require_sha256(plan, "input_sha256", "plan") != input_sha256:
        raise ValueError("plan input_sha256 does not match mission")
    observed_input = decision.get("observed_input_sha256")
    if observed_input is not None and require_sha256(decision, "observed_input_sha256", "decision") != input_sha256:
        raise ValueError("decision observed_input_sha256 does not match mission")

    authority_status = "SUCCEEDED" if decision.get("allowed") is True else "BLOCKED"
    plan_sha256 = require_sha256(decision, "plan_sha256", "decision")
    evidence_sha256 = require_sha256(event, "evidence_sha256", "event")

    connection = sqlite3.connect(db_path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        with connection:
            connection.execute(
                """
                INSERT INTO tower_mission(
                  mission_id, objective, input_sha256, plan_sha256, authority_status
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(mission_id) DO UPDATE SET
                  objective = excluded.objective,
                  input_sha256 = excluded.input_sha256,
                  plan_sha256 = excluded.plan_sha256,
                  authority_status = excluded.authority_status
                """,
                (
                    mission_id,
                    require_string(mission, "objective", "mission"),
                    input_sha256,
                    plan_sha256,
                    authority_status,
                ),
            )
            stage = require_string(event, "stage", "event")
            connection.execute(
                "DELETE FROM tower_event WHERE mission_id = ? AND stage = ?",
                (mission_id, stage),
            )
            connection.execute(
                """
                INSERT INTO tower_event(mission_id, stage, status, evidence_sha256)
                VALUES (?, ?, ?, ?)
                """,
                (
                    mission_id,
                    stage,
                    require_string(event, "status", "event"),
                    evidence_sha256,
                ),
            )
        row = connection.execute(
            """
            SELECT m.mission_id, m.objective, m.input_sha256, m.plan_sha256,
                   m.authority_status, e.stage, e.status, e.evidence_sha256
            FROM tower_mission AS m
            JOIN tower_event AS e ON e.mission_id = m.mission_id
            WHERE m.mission_id = ?
            ORDER BY e.event_id DESC
            LIMIT 1
            """,
            (mission_id,),
        ).fetchone()
    finally:
        connection.close()
    if row is None:
        raise RuntimeError("SQL persistence readback returned no mission chain")
    readback = {
        "mission_id": row[0],
        "objective": row[1],
        "input_sha256": row[2],
        "plan_sha256": row[3],
        "authority_status": row[4],
        "stage": row[5],
        "status": row[6],
        "evidence_sha256": row[7],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(readback, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(readback, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
