#!/usr/bin/env python3
"""Execute the flagship polyglot pipeline with strict proof or explicit blockers."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from tower.registry import load_registry

WORK = ROOT / "build" / "flagship"
MISSION_FIELDS = {
    "mission_id",
    "objective",
    "required_capabilities",
    "preferred_interfaces",
    "maximum_action",
}
REQUIRED_STAGES = {
    "typescript_compile",
    "typescript_ingress",
    "python_planner",
    "rust_authority",
    "go_compile",
    "go_telemetry",
    "sql_state",
    "wasm_sandbox",
    "lean_invariant",
    "protobuf_contracts",
}


def run(argv: list[str], *, cwd: Path = ROOT) -> dict:
    """Execute one argv-safe stage and return bounded evidence."""
    try:
        completed = subprocess.run(
            argv, cwd=cwd, text=True, capture_output=True, timeout=180, check=False
        )
        return {
            "argv": argv,
            "returncode": completed.returncode,
            "stdout": completed.stdout[-3000:],
            "stderr": completed.stderr[-3000:],
            "status": "VERIFIED" if completed.returncode == 0 else "FAILED",
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "argv": argv,
            "returncode": None,
            "stdout": (exc.stdout or "")[-3000:] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[-3000:] if isinstance(exc.stderr, str) else "",
            "status": "FAILED_TIMEOUT",
        }
    except OSError as exc:
        return {
            "argv": argv,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "status": "FAILED_SPAWN",
        }


def blocker(tool: str, stage: str) -> dict:
    """Return an exact toolchain blocker."""
    return {
        "stage": stage,
        "status": "BLOCKED_TOOLCHAIN",
        "blocker": f"Required executable not found: {tool}",
    }


def dependency_block(stage: str, dependency: str) -> dict:
    """Return an exact upstream-dependency blocker."""
    return {
        "stage": stage,
        "status": "BLOCKED_DEPENDENCY",
        "blocker": f"Required upstream artifact is unavailable: {dependency}",
    }


def _require_string(payload: dict, field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"mission.{field} must be a non-empty string")
    return value.strip()


def _require_string_list(payload: dict, field: str) -> list[str]:
    value = payload.get(field)
    if not isinstance(value, list) or not value or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise ValueError(f"mission.{field} must be a non-empty string list")
    return [item.strip() for item in value]


def canonical_mission(payload: dict) -> dict:
    """Validate and normalize the cross-language mission hash contract."""
    unsigned = dict(payload)
    unsigned.pop("input_sha256", None)
    unknown = sorted(set(unsigned) - MISSION_FIELDS)
    missing = sorted(MISSION_FIELDS - set(unsigned))
    if unknown:
        raise ValueError("mission contains unsupported fields: " + ", ".join(unknown))
    if missing:
        raise ValueError("mission is missing required fields: " + ", ".join(missing))
    maximum_action = _require_string(unsigned, "maximum_action")
    if maximum_action not in {"read", "plan", "write_internal", "external"}:
        raise ValueError("mission.maximum_action is unsupported")
    # The explicit field order and compact separators match the TypeScript
    # ingress implementation byte-for-byte for UTF-8 mission content.
    return {
        "maximum_action": maximum_action,
        "mission_id": _require_string(unsigned, "mission_id"),
        "objective": _require_string(unsigned, "objective"),
        "preferred_interfaces": _require_string_list(unsigned, "preferred_interfaces"),
        "required_capabilities": _require_string_list(unsigned, "required_capabilities"),
    }


def canonical_json_sha256(payload: dict) -> str:
    canonical = json.dumps(
        canonical_mission(payload),
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def write_fallback_mission(source: Path, mission: Path) -> None:
    """Create an explicitly labeled Python fallback for diagnostic runs only."""
    payload = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("mission input must be an object")
    canonical = canonical_mission(payload)
    canonical["input_sha256"] = canonical_json_sha256(canonical)
    mission.write_text(
        json.dumps(canonical, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    """Parse strict-by-default pipeline options."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-blocked",
        action="store_true",
        help="permit tool/dependency blockers for diagnostic portability runs",
    )
    return parser.parse_args()


def main() -> int:
    """Run all declared floors from a clean work directory."""
    args = parse_args()
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    results: list[dict] = []
    source = ROOT / "flagship" / "mission.input.json"
    source_payload = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(source_payload, dict):
        raise ValueError("mission input must be an object")
    expected_input_sha256 = canonical_json_sha256(source_payload)
    expected_maximum_action = canonical_mission(source_payload)["maximum_action"]

    registry = load_registry()
    expected_registry_sha256 = hashlib.sha256(registry.canonical_bytes()).hexdigest()
    allowed_technology_ids = ",".join(sorted(technology["id"] for technology in registry.technologies))

    mission = WORK / "mission.json"
    plan = WORK / "plan.json"
    decision = WORK / "decision.json"
    event = WORK / "event.json"
    db = WORK / "tower.db"
    sql_readback = WORK / "sql.readback.json"

    if shutil.which("tsc") and shutil.which("node"):
        ts_out = WORK / "typescript"
        ts_out.mkdir()
        compile_result = run([
            "tsc", "--strict", "--target", "ES2022", "--module", "commonjs",
            "--outDir", str(ts_out), "flagship/typescript/ingress.ts",
        ])
        compile_result["stage"] = "typescript_compile"
        results.append(compile_result)
        if compile_result["status"] == "VERIFIED":
            ingress = run([
                "node", str(ts_out / "ingress.js"), str(source), str(mission),
            ])
            ingress["stage"] = "typescript_ingress"
            results.append(ingress)
        else:
            results.append(dependency_block("typescript_ingress", "typescript_compile"))
    else:
        results.append(blocker("tsc/node", "typescript_compile"))
        results.append(dependency_block("typescript_ingress", "typescript_compile"))

    if not mission.is_file() and args.allow_blocked:
        write_fallback_mission(source, mission)
        results.append({"stage": "python_ingress_fallback", "status": "FALLBACK"})

    if mission.is_file():
        mission_payload = json.loads(mission.read_text(encoding="utf-8"))
        if not isinstance(mission_payload, dict) or mission_payload.get("input_sha256") != expected_input_sha256:
            planner = {
                "stage": "python_planner",
                "status": "FAILED",
                "blocker": "TypeScript ingress hash does not match the canonical source mission",
            }
            results.append(planner)
        else:
            planner = run([sys.executable, "flagship/python/planner.py", str(mission), str(plan)])
            planner["stage"] = "python_planner"
            results.append(planner)
    else:
        planner = dependency_block("python_planner", "mission.json")
        results.append(planner)

    if plan.is_file() and planner["status"] == "VERIFIED" and shutil.which("cargo"):
        authority = run([
            "cargo", "run", "--quiet", "--manifest-path", "flagship/rust/Cargo.toml",
            "--", str(plan), str(decision), expected_registry_sha256,
            expected_input_sha256, expected_maximum_action, allowed_technology_ids,
        ])
        authority["stage"] = "rust_authority"
        results.append(authority)
    elif plan.is_file() and planner["status"] == "VERIFIED":
        results.append(blocker("cargo", "rust_authority"))
    else:
        results.append(dependency_block("rust_authority", "verified plan.json"))

    go_binary = WORK / "tower-telemetry"
    if shutil.which("go"):
        compile_go = run(["go", "build", "-o", str(go_binary), "flagship/go/telemetry.go"])
        compile_go["stage"] = "go_compile"
        results.append(compile_go)
    else:
        compile_go = blocker("go", "go_compile")
        results.append(compile_go)
    if compile_go["status"] == "VERIFIED" and decision.is_file():
        telemetry = run([str(go_binary), str(decision), str(event)])
        telemetry["stage"] = "go_telemetry"
        results.append(telemetry)
    elif compile_go["status"] != "VERIFIED":
        results.append(dependency_block("go_telemetry", "go_compile"))
    else:
        results.append(dependency_block("go_telemetry", "decision.json"))

    if all(path.is_file() for path in (mission, plan, decision, event)):
        sql_result = run([
            sys.executable,
            "flagship/python/persist_state.py",
            "flagship/sql/state.sql",
            str(db),
            str(mission),
            str(decision),
            str(event),
            str(plan),
            str(sql_readback),
        ])
        sql_result["stage"] = "sql_state"
        results.append(sql_result)
    else:
        results.append(dependency_block("sql_state", "mission/plan/decision/event chain"))

    if shutil.which("wat2wasm"):
        wasm = run([
            "wat2wasm", "flagship/wat/sandbox.wat", "-o", str(WORK / "sandbox.wasm")
        ])
        wasm["stage"] = "wasm_sandbox"
        results.append(wasm)
    else:
        results.append(blocker("wat2wasm", "wasm_sandbox"))

    if shutil.which("lake"):
        lean = run(["lake", "env", "lean", "flagship/lean4/invariant.lean"])
        lean["stage"] = "lean_invariant"
        results.append(lean)
    else:
        results.append(blocker("lake", "lean_invariant"))

    if shutil.which("protoc"):
        descriptor = WORK / "tower-contracts.pb"
        protobuf = run([
            "protoc",
            f"--descriptor_set_out={descriptor}",
            "--include_imports",
            "flagship/contracts/mission.proto",
            "integrations/megamind/tower_adapter.proto",
            "proto/tower.proto",
        ])
        protobuf["stage"] = "protobuf_contracts"
        results.append(protobuf)
    else:
        results.append(blocker("protoc", "protobuf_contracts"))

    mission_payload = json.loads(mission.read_text(encoding="utf-8")) if mission.is_file() else {}
    report = {
        "pipeline_id": "tower-polyglot-mission-v1",
        "mission_id": mission_payload.get("mission_id", "unavailable") if isinstance(mission_payload, dict) else "unavailable",
        "expected_registry_sha256": expected_registry_sha256,
        "expected_input_sha256": expected_input_sha256,
        "expected_maximum_action": expected_maximum_action,
        "strict": not args.allow_blocked,
        "results": results,
    }
    report_bytes = json.dumps(report, separators=(",", ":"), sort_keys=True).encode("utf-8")
    report["report_sha256"] = hashlib.sha256(report_bytes).hexdigest()
    (WORK / "pipeline.report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))

    required_results = {row["stage"]: row for row in results if row.get("stage") in REQUIRED_STAGES}
    missing = sorted(REQUIRED_STAGES - set(required_results))
    failed = [
        row for row in results
        if str(row.get("status", "")).startswith("FAILED")
    ]
    blocked = [
        row for row in required_results.values()
        if str(row.get("status", "")).startswith("BLOCKED_")
    ]
    nonverified = [
        row for row in required_results.values()
        if row.get("status") != "VERIFIED"
    ]
    if failed or missing:
        return 1
    if args.allow_blocked:
        return 0
    return 1 if blocked or nonverified else 0


if __name__ == "__main__":
    raise SystemExit(main())
