from pathlib import Path
import json
import subprocess
import sys

from tower.registry import REPO_ROOT


def test_python_planner_traverses_tower_adapter(tmp_path):
    source = REPO_ROOT / "flagship" / "mission.input.json"
    mission = tmp_path / "mission.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["input_sha256"] = "0" * 64
    mission.write_text(json.dumps(payload), encoding="utf-8")
    plan = tmp_path / "plan.json"
    completed = subprocess.run(
        [sys.executable, str(REPO_ROOT / "flagship/python/planner.py"), str(mission), str(plan)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    result = json.loads(plan.read_text(encoding="utf-8"))
    assert result["technology_ids"]
    assert result["agent_ids"]
    assert result["piston_ids"]
    assert len(result["tower_registry_sha256"]) == 64


def test_flagship_contracts_cover_all_stages():
    assert (REPO_ROOT / "flagship/contracts/mission.proto").is_file()
    assert (REPO_ROOT / "flagship/typescript/ingress.ts").is_file()
    assert (REPO_ROOT / "flagship/python/planner.py").is_file()
    assert (REPO_ROOT / "flagship/rust/src/main.rs").is_file()
    assert (REPO_ROOT / "flagship/go/telemetry.go").is_file()
    assert (REPO_ROOT / "flagship/sql/state.sql").is_file()
    assert (REPO_ROOT / "flagship/wat/sandbox.wat").is_file()
    assert (REPO_ROOT / "flagship/lean4/invariant.lean").is_file()
