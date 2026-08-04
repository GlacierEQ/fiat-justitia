#!/usr/bin/env python3
"""Plan a mission through the canonical Tower-to-Megamind adapter."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))

from integrations.megamind.adapter import TechnologyRequest, select_technologies


def require_string(payload: dict, field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"mission.{field} must be a non-empty string")
    return value


def require_string_list(payload: dict, field: str) -> tuple[str, ...]:
    value = payload.get(field)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"mission.{field} must be a non-empty string list")
    return tuple(item.strip() for item in value)


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: planner <mission.json> <plan.json>")
    input_path, output_path = map(Path, sys.argv[1:3])
    mission = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(mission, dict):
        raise ValueError("mission must be a JSON object")
    plan = select_technologies(
        TechnologyRequest(
            mission_id=require_string(mission, "mission_id"),
            capabilities=require_string_list(mission, "required_capabilities"),
            interfaces=require_string_list(mission, "preferred_interfaces"),
            minimum_proof_class="compile",
        )
    )
    if plan["unmatched_capabilities"] or not plan["technology_ids"]:
        raise RuntimeError(
            "Tower could not cover all mission capabilities: "
            + ", ".join(plan["unmatched_capabilities"])
        )
    plan["input_sha256"] = require_string(mission, "input_sha256")
    plan["maximum_action"] = require_string(mission, "maximum_action")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"stage": "planner", "technologies": plan["technology_ids"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
