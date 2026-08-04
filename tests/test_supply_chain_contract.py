from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PERMANENT_WORKFLOWS = [
    ROOT / ".github/workflows/tower.yml",
    ROOT / ".github/workflows/ci.yml",
    ROOT / ".github/workflows/spiral.yml",
    ROOT / ".github/workflows/advanced-exhibits.yml",
    ROOT / ".github/workflows/nervous-system-contract.yml",
    ROOT / ".github/workflows/branch-hygiene.yml",
    ROOT / ".github/workflows/main-ruleset-contract.yml",
]
REQUIRED_CONTEXTS = {
    "required-advanced-exhibit-gate",
    "required-nervous-system-contract",
    "required-quality-gate",
    "required-spiral-verification",
    "required-tower-verification",
}


def test_permanent_actions_are_pinned_to_full_commit_shas() -> None:
    for workflow in PERMANENT_WORKFLOWS:
        text = workflow.read_text(encoding="utf-8")
        uses = re.findall(r"^\s*-?\s*uses:\s*([^\s#]+)", text, re.MULTILINE)
        assert uses, workflow
        for action in uses:
            assert re.search(r"@[0-9a-f]{40}$", action), (workflow.name, action)


def test_ci_lock_is_exact_and_hash_verified() -> None:
    text = (ROOT / "requirements/ci.lock").read_text(encoding="utf-8")
    packages = re.findall(r"^([A-Za-z0-9_.-]+)==([^\s\\]+)", text, re.MULTILINE)
    hashes = re.findall(r"--hash=sha256:([0-9a-f]{64})", text)
    assert len(packages) >= 8
    assert len(hashes) == len(packages)
    assert "--only-binary=:all:" in text


def test_branch_hygiene_has_one_exact_head_deletion_boundary() -> None:
    text = (ROOT / ".github/workflows/branch-hygiene.yml").read_text(encoding="utf-8")
    assert "pull_request:" in text and "types: [closed]" in text
    assert "EXPECTED_SHA" in text and "remote_sha" in text
    assert "git branch -r --merged" not in text
    assert "tower integrity generate" not in text
    assert "git push origin HEAD:main" not in text
    assert "git/refs/heads/${BRANCH}" in text


def test_ruleset_contexts_are_emitted_by_workflows() -> None:
    contract = json.loads(
        (ROOT / "governance/main-ruleset.required.json").read_text(encoding="utf-8")
    )
    status_rule = next(rule for rule in contract["rules"] if rule["type"] == "required_status_checks")
    contexts = {
        row["context"]
        for row in status_rule["parameters"]["required_status_checks"]
    }
    assert contexts == REQUIRED_CONTEXTS
    workflow_text = "\n".join(path.read_text(encoding="utf-8") for path in PERMANENT_WORKFLOWS)
    for context in contexts:
        assert f"name: {context}" in workflow_text


def test_tower_receipts_have_oidc_attestation_boundary() -> None:
    text = (ROOT / ".github/workflows/tower.yml").read_text(encoding="utf-8")
    assert "id-token: write" in text
    assert "attestations: write" in text
    assert "actions/attest-build-provenance@" in text
    for subject in (
        "artifacts/build-report.json",
        "artifacts/benchmarks.json",
        "artifacts/proof-report.json",
        "artifacts/tower_receipt.json",
    ):
        assert subject in text
