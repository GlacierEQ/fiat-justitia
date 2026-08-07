from __future__ import annotations

import re
from pathlib import Path

from tower.registry import REPO_ROOT, load_registry, validate_registry


def test_every_floor_has_one_semantic_claim_contract() -> None:
    registry = load_registry()
    tech_ids = {tech["id"] for tech in registry.technologies if "advanced_example" in tech}
    if tech_ids:
        assert set(registry.claim_contracts).issuperset(tech_ids)


def test_claim_contract_source_assertions_match_advanced_exhibits() -> None:
    registry = load_registry()
    for tech in registry.technologies:
        if "advanced_example" not in tech or tech.get("advanced_example", "").startswith("N/A"):
            continue
        contract = registry.claim_contract_for(tech["id"])
        if not contract:
            continue
        adv_path = REPO_ROOT / tech["advanced_example"]
        if not adv_path.is_file():
            continue
        text = adv_path.read_text(encoding="utf-8")
        for pattern in contract.get("required_source_patterns", []):
            assert re.search(pattern, text, re.IGNORECASE | re.MULTILINE), (
                tech["id"], pattern, Path(tech["advanced_example"]).name
            )


def test_claim_contracts_expose_failure_receipt_and_overclaim_boundaries() -> None:
    registry = load_registry()
    for tech_id, contract in registry.claim_contracts.items():
        assert len(contract["expected_failure_cases"]) >= 3, tech_id
        assert len(contract["required_receipt_fields"]) >= 3, tech_id
        assert contract["forbidden_claim_patterns"], tech_id
        for pattern in contract["forbidden_claim_patterns"]:
            re.compile(pattern, re.IGNORECASE)
