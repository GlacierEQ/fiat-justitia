"""Tests for the civilization-scale Spiral Engine."""
from __future__ import annotations

import hashlib
from copy import deepcopy

from tower.spiral import (
    DOMAIN_TAXONOMY,
    build_admission_receipt,
    generate_civilization_question,
    verify_admission_receipt,
)


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _candidate() -> dict:
    return {
        "capability_id": "spiral.civilization-synthesis.v1",
        "summary": (
            "Generate whole-system questions and evidence-bound activation decisions "
            "across every civilization domain."
        ),
        "scope": "civilization",
        "risk_level": "moderate",
        "affected_domains": list(DOMAIN_TAXONOMY),
        "evidence": [
            {"id": "unit-tests", "kind": "test", "sha256": _digest("unit-tests")},
            {"id": "contract", "kind": "specification", "sha256": _digest("contract")},
            {"id": "example", "kind": "executable-example", "sha256": _digest("example")},
        ],
        "controls": {
            "owner": "Tower Governance",
            "approval_mode": "human-and-machine",
            "human_override": True,
            "audit_log": True,
            "rollback_plan": "Disable the capability and invalidate its admission receipt.",
            "metrics": ["domain_coverage", "receipt_verification_rate"],
        },
    }


def test_question_is_replayable_en_us_and_covers_all_domains():
    first = generate_civilization_question("civilization")
    second = generate_civilization_question("civilization")
    assert first == second
    assert first["locale"] == "en-US"
    assert first["scope"] == "civilization"
    assert set(first["domains"]) == set(DOMAIN_TAXONOMY)
    assert len(first["question_sha256"]) == 64
    assert first["question"].endswith("generation?")


def test_complete_civilization_capability_is_admitted():
    receipt = build_admission_receipt(_candidate())
    assert receipt["decision"] == "ADMIT"
    assert receipt["evaluation"]["score"] == 1.0
    assert receipt["evaluation"]["blockers"] == []
    assert verify_admission_receipt(receipt)["ok"]


def test_missing_domain_is_rejected_with_exact_blocker():
    candidate = _candidate()
    candidate["affected_domains"].remove("law")
    receipt = build_admission_receipt(candidate)
    assert receipt["decision"] == "REJECT"
    assert "MISSING_CIVILIZATION_DOMAINS:law" in receipt["evaluation"]["blockers"]


def test_receipt_tampering_is_detected():
    receipt = build_admission_receipt(_candidate())
    tampered = deepcopy(receipt)
    tampered["decision"] = "REJECT"
    verification = verify_admission_receipt(tampered)
    assert not verification["ok"]
    assert "RECEIPT_HASH_MISMATCH" in verification["errors"]
