from __future__ import annotations

import json
from pathlib import Path

from scripts.verify_main_ruleset import compare

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "governance" / "main-ruleset.required.json"


def required_contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_main_ruleset_contract_has_stable_required_contexts() -> None:
    contract = required_contract()
    assert contract["enforcement"] == "active"
    assert contract["conditions"]["ref_name"]["include"] == ["refs/heads/main"]
    rules = {rule["type"]: rule for rule in contract["rules"]}
    assert {"deletion", "non_fast_forward", "required_pull_request", "required_status_checks"} <= set(rules)
    contexts = {
        row["context"]
        for row in rules["required_status_checks"]["parameters"]["required_status_checks"]
    }
    assert contexts == {
        "required-advanced-exhibit-gate",
        "required-nervous-system-contract",
        "required-quality-gate",
        "required-spiral-verification",
        "required-tower-verification",
    }


def test_ruleset_comparison_rejects_missing_status_context() -> None:
    contract = required_contract()
    live = json.loads(json.dumps(contract))
    live["id"] = 1
    live["rules"][-1]["parameters"]["required_status_checks"].pop()
    errors = compare(contract, live)
    assert any("missing required status contexts" in error for error in errors)


def test_ruleset_comparison_accepts_exact_contract() -> None:
    contract = required_contract()
    live = json.loads(json.dumps(contract))
    live["id"] = 1
    assert compare(contract, live) == []
