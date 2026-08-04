"""Civilization-scale synthesis and capability admission for the Tower.

The Spiral Engine has two deterministic responsibilities:

1. Generate a cross-domain question that forces whole-system reasoning.
2. Admit or reject a capability and bind the decision to a SHA-256 receipt.

It deliberately performs no network calls and has no model dependency. A model may
answer the generated question, but the admission boundary remains inspectable code.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import secrets
from pathlib import Path
from typing import Any, Mapping

ENGINE_VERSION = "1.0.0-alpha.1"
RECEIPT_SCHEMA = "glaciereq.spiral-admission-receipt.v1"
QUESTION_SCHEMA = "glaciereq.spiral-civilization-question.v1"
ADMISSION_THRESHOLD = 0.85

DOMAIN_TAXONOMY = (
    "science",
    "technology",
    "health",
    "environment",
    "economics",
    "law",
    "governance",
    "history",
    "culture",
    "art",
    "education",
    "ethics",
    "infrastructure",
    "security",
    "information",
    "psychology",
    "demographics",
    "geopolitics",
)

_QUESTION_LENSES = (
    "create the strongest positive feedback loop",
    "reduce systemic fragility without centralizing unchecked power",
    "improve human flourishing while preserving future optionality",
    "increase truth, capability, and coordination without exporting hidden harm",
    "turn a local breakthrough into durable civilization-wide benefit",
)

_TIME_HORIZONS = (
    "the next decade",
    "one human generation",
    "the next century",
    "a crisis-to-recovery cycle",
    "the transition from scarcity management to regenerative abundance",
)

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _normalized_domains(raw: Any) -> tuple[list[str], list[str]]:
    if not isinstance(raw, list):
        return [], []
    normalized: list[str] = []
    unknown: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            unknown.append(repr(item))
            continue
        domain = item.strip().lower()
        if domain in DOMAIN_TAXONOMY:
            if domain not in normalized:
                normalized.append(domain)
        elif domain:
            unknown.append(domain)
    return normalized, unknown


def generate_civilization_question(
    seed: str | int | None = None,
    prompt_hint: str | None = None,
) -> dict[str, Any]:
    """Generate one en-US question spanning every civilization domain.

    Supplying a seed makes the result reproducible. Omitting it creates a fresh
    seed while still returning that seed in the envelope for replay. An optional
    prompt_hint integrates model synthesis focus into the envelope.
    """
    effective_seed = str(seed) if seed is not None else secrets.token_hex(16)
    rng = random.Random(effective_seed)
    domains = list(DOMAIN_TAXONOMY)
    rng.shuffle(domains)
    lens = rng.choice(_QUESTION_LENSES)
    horizon = rng.choice(_TIME_HORIZONS)
    domain_phrase = ", ".join(domains[:-1]) + f", and {domains[-1]}"
    
    base_question = (
        f"Across {domain_phrase}, which intervention is most likely to {lens} "
        f"over {horizon}, what evidence would falsify it, and how would you prevent "
        "its benefits from shifting hidden costs to another domain, population, or generation?"
    )
    
    if prompt_hint and prompt_hint.strip():
        question = f"[Focus: {prompt_hint.strip()}] {base_question}"
    else:
        question = base_question

    envelope: dict[str, Any] = {
        "schema": QUESTION_SCHEMA,
        "engine_version": ENGINE_VERSION,
        "locale": "en-US",
        "scope": "civilization",
        "seed": effective_seed,
        "domains": domains,
        "question": question,
    }
    if prompt_hint and prompt_hint.strip():
        envelope["prompt_hint"] = prompt_hint.strip()

    envelope["question_sha256"] = _sha256(envelope)
    return envelope


def _evidence_state(raw: Any) -> tuple[int, list[str]]:
    if not isinstance(raw, list):
        return 0, ["EVIDENCE_MUST_BE_A_LIST"]
    valid = 0
    blockers: list[str] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(raw):
        if not isinstance(item, Mapping):
            blockers.append(f"EVIDENCE_{index}_MUST_BE_AN_OBJECT")
            continue
        evidence_id = item.get("id")
        kind = item.get("kind")
        digest = item.get("sha256")
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            blockers.append(f"EVIDENCE_{index}_MISSING_ID")
            continue
        if evidence_id in seen_ids:
            blockers.append(f"EVIDENCE_DUPLICATE_ID:{evidence_id}")
            continue
        seen_ids.add(evidence_id)
        if not isinstance(kind, str) or not kind.strip():
            blockers.append(f"EVIDENCE_{index}_MISSING_KIND")
            continue
        if not isinstance(digest, str) or not _SHA256_RE.fullmatch(digest):
            blockers.append(f"EVIDENCE_{index}_INVALID_SHA256")
            continue
        valid += 1
    if valid == 0:
        blockers.append("NO_VALID_EVIDENCE")
    return valid, blockers


def evaluate_capability(candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate a capability against civilization-scale activation controls."""
    capability_id = candidate.get("capability_id")
    summary = candidate.get("summary")
    scope = candidate.get("scope", "civilization")
    risk_level = str(candidate.get("risk_level", "moderate")).strip().lower()

    blockers: list[str] = []
    if not isinstance(capability_id, str) or not capability_id.strip():
        blockers.append("MISSING_CAPABILITY_ID")
    if not isinstance(summary, str) or len(summary.strip()) < 20:
        blockers.append("SUMMARY_TOO_SHORT")
    if scope != "civilization":
        blockers.append("UNSUPPORTED_SCOPE")

    domains, unknown_domains = _normalized_domains(candidate.get("affected_domains"))
    if unknown_domains:
        blockers.extend(f"UNKNOWN_DOMAIN:{domain}" for domain in unknown_domains)
    missing_domains = [domain for domain in DOMAIN_TAXONOMY if domain not in domains]
    if missing_domains:
        blockers.append("MISSING_CIVILIZATION_DOMAINS:" + ",".join(missing_domains))

    valid_evidence, evidence_blockers = _evidence_state(candidate.get("evidence"))
    blockers.extend(evidence_blockers)

    controls = candidate.get("controls")
    controls = controls if isinstance(controls, Mapping) else {}
    owner = controls.get("owner")
    approval_mode = controls.get("approval_mode")
    human_override = controls.get("human_override") is True
    audit_log = controls.get("audit_log") is True
    rollback_plan = controls.get("rollback_plan")
    metrics = controls.get("metrics")

    control_checks = {
        "owner": isinstance(owner, str) and bool(owner.strip()),
        "approval_mode": approval_mode in {"human", "human-and-machine"},
        "human_override": human_override,
        "audit_log": audit_log,
        "rollback_plan": isinstance(rollback_plan, str) and len(rollback_plan.strip()) >= 12,
        "metrics": isinstance(metrics, list)
        and len(metrics) >= 2
        and all(isinstance(metric, str) and metric.strip() for metric in metrics),
    }
    for control, ok in control_checks.items():
        if not ok:
            blockers.append(f"MISSING_CONTROL:{control}")

    if risk_level not in {"low", "moderate", "high", "critical"}:
        blockers.append("INVALID_RISK_LEVEL")
    if risk_level in {"high", "critical"} and not human_override:
        blockers.append("HIGH_RISK_REQUIRES_HUMAN_OVERRIDE")

    domain_score = len(domains) / len(DOMAIN_TAXONOMY)
    evidence_score = min(valid_evidence / 3, 1.0)
    controls_score = sum(control_checks.values()) / len(control_checks)
    score = round((0.40 * domain_score) + (0.30 * evidence_score) + (0.30 * controls_score), 6)
    decision = "ADMIT" if not blockers and score >= ADMISSION_THRESHOLD else "REJECT"

    return {
        "decision": decision,
        "score": score,
        "threshold": ADMISSION_THRESHOLD,
        "scope": scope,
        "risk_level": risk_level,
        "domain_coverage": {
            "covered": domains,
            "missing": missing_domains,
            "ratio": round(domain_score, 6),
        },
        "evidence": {
            "valid_count": valid_evidence,
            "score": round(evidence_score, 6),
        },
        "controls": {
            **control_checks,
            "score": round(controls_score, 6),
        },
        "blockers": sorted(set(blockers)),
    }


def build_admission_receipt(candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic, tamper-evident activation receipt."""
    candidate_object = dict(candidate)
    evaluation = evaluate_capability(candidate_object)
    payload: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA,
        "engine_version": ENGINE_VERSION,
        "capability_id": candidate_object.get("capability_id"),
        "candidate_sha256": _sha256(candidate_object),
        "decision": evaluation["decision"],
        "evaluation": evaluation,
    }
    payload["receipt_id"] = f"spiral:{_sha256(payload)[:24]}"
    payload["receipt_sha256"] = _sha256(payload)
    return payload


def verify_admission_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Verify the receipt hash and minimum structural invariants."""
    candidate = dict(receipt)
    supplied = candidate.pop("receipt_sha256", None)
    expected = _sha256(candidate)
    errors: list[str] = []
    if receipt.get("schema") != RECEIPT_SCHEMA:
        errors.append("INVALID_SCHEMA")
    if receipt.get("engine_version") != ENGINE_VERSION:
        errors.append("ENGINE_VERSION_MISMATCH")
    if receipt.get("decision") not in {"ADMIT", "REJECT"}:
        errors.append("INVALID_DECISION")
    if not isinstance(supplied, str) or supplied != expected:
        errors.append("RECEIPT_HASH_MISMATCH")
    receipt_id = receipt.get("receipt_id")
    if not isinstance(receipt_id, str) or not receipt_id.startswith("spiral:"):
        errors.append("INVALID_RECEIPT_ID")
    return {
        "ok": not errors,
        "errors": errors,
        "expected_sha256": expected,
        "supplied_sha256": supplied,
    }


def read_json_object(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"JSON object not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid JSON object: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(dict(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
