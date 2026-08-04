import json
import subprocess
import sys
from pathlib import Path

import pytest

from tower import integrity as integrity_module
from tower.proofs import _build_statuses
from tower.registry import REPO_ROOT


def test_proof_statuses_reject_duplicate_technology_rows():
    with pytest.raises(ValueError, match="duplicate build result for technology: rust"):
        _build_statuses(
            {
                "results": [
                    {"technology_id": "rust", "status": "VERIFIED"},
                    {"technology_id": "rust", "status": "FAILED"},
                ]
            }
        )


def test_flagship_sql_persists_and_reads_back_the_real_chain(tmp_path):
    input_sha256 = "d" * 64
    mission = {
        "mission_id": "mission-test-001",
        "objective": "prove the SQL persistence boundary",
        "input_sha256": input_sha256,
    }
    plan = {
        "mission_id": mission["mission_id"],
        "technology_ids": ["sql"],
        "tower_registry_sha256": "a" * 64,
        "input_sha256": input_sha256,
    }
    decision = {
        "mission_id": mission["mission_id"],
        "allowed": True,
        "reason": "verified",
        "plan_sha256": "b" * 64,
        "observed_input_sha256": input_sha256,
    }
    event = {
        "mission_id": mission["mission_id"],
        "stage": "authority",
        "status": "SUCCEEDED",
        "evidence_sha256": "c" * 64,
    }
    paths = {}
    for name, payload in (
        ("mission", mission),
        ("plan", plan),
        ("decision", decision),
        ("event", event),
    ):
        path = tmp_path / f"{name}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        paths[name] = path
    output = tmp_path / "readback.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "flagship/python/persist_state.py"),
            str(REPO_ROOT / "flagship/sql/state.sql"),
            str(tmp_path / "tower.db"),
            str(paths["mission"]),
            str(paths["decision"]),
            str(paths["event"]),
            str(paths["plan"]),
            str(output),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    readback = json.loads(output.read_text(encoding="utf-8"))
    assert readback["mission_id"] == mission["mission_id"]
    assert readback["authority_status"] == "SUCCEEDED"
    assert readback["input_sha256"] == input_sha256
    assert readback["plan_sha256"] == decision["plan_sha256"]
    assert readback["evidence_sha256"] == event["evidence_sha256"]


def test_rust_authority_compares_observed_and_expected_registry_hashes():
    source = (REPO_ROOT / "flagship/rust/src/main.rs").read_text(encoding="utf-8")
    assert "expected_registry_sha256 == observed_registry_sha256" in source
    assert "expected_input_sha256 == observed_input_sha256" in source
    assert "process::exit(3)" in source


def test_flagship_is_strict_by_default_and_executes_contracts():
    source = (REPO_ROOT / "flagship/run_pipeline.py").read_text(encoding="utf-8")
    assert '"--allow-blocked"' in source
    assert '"protobuf_contracts"' in source
    assert '"sql_state"' in source
    assert "return 1 if blocked or nonverified else 0" in source


def test_integrity_ignores_reproducible_lake_cache(tmp_path, monkeypatch):
    governed = tmp_path / "lean-toolchain"
    governed.write_text("leanprover/lean4:v4.15.0\n", encoding="utf-8")
    cache = tmp_path / ".lake" / "lakefile.olean"
    cache.parent.mkdir(parents=True)
    cache.write_bytes(b"reproducible compiler cache")
    monkeypatch.setattr(integrity_module, "REPO_ROOT", tmp_path)
    hashes = integrity_module.collect_hashes()
    assert hashes == {"lean-toolchain": integrity_module.hash_file(governed)}
