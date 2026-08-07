"""Tower-to-Megamind technology selection adapter."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from tower.registry import TowerRegistry, load_registry


@dataclass(frozen=True)
class TechnologyRequest:
    mission_id: str
    capabilities: tuple[str, ...]
    interfaces: tuple[str, ...] = ()
    minimum_proof_class: str = ""


_PROOF_ORDER = {
    "illustrative": 0,
    "draft": 0,
    "emergency": 0,
    "researched": 1,
    "templated": 1,
    "compile": 1,
    "precedent_verified": 2,
    "behavioral": 2,
    "filed": 3,
    "benchmark": 3,
    "hardware": 3,
    "argued": 4,
    "ruled": 4,
    "integration": 4,
    "appellate_reviewed": 5,
    "supreme_certified": 5,
    "formal": 5,
    "constitutional": 6,
}
_GATED_STATES = {"hardware_gated", "toolchain_gated", "service_gated"}
_CAPABILITY_ALIASES = {
    "coding": {"code", "coding", "compiler", "program", "software", "application", "development"},
    "evidence": {"evidence", "proof", "receipt", "audit", "verification", "integrity", "provenance"},
    "tool": {"tool", "tooling", "toolchain", "automation", "orchestration", "cli", "gateway"},
}


def _words(value: str) -> set[str]:
    return {token for token in re.split(r"[^a-z0-9]+", value.casefold()) if token}


def _tokens(row: dict) -> set[str]:
    values: list[str] = [
        str(row.get("id", "")), str(row.get("name", "")), str(row.get("category", "")),
        str(row.get("artifact_type", "")), str(row.get("what", "")), str(row.get("where", "")),
        str(row.get("when", "")), str(row.get("why", "")), str(row.get("how", "")),
        str(row.get("evidence_state", "")), str(row.get("proof_class", "")),
        *[str(item) for item in row.get("interfaces", []) if isinstance(item, str)],
    ]
    return {token for value in values for token in _words(value)}


def _capability_matches(capability: str, tokens: set[str]) -> bool:
    normalized = capability.casefold().strip()
    candidates = _CAPABILITY_ALIASES.get(normalized, {normalized})
    return any(
        candidate in tokens
        or (len(candidate) >= 4 and any(token.startswith(candidate) or candidate.startswith(token) for token in tokens if len(token) >= 4))
        for candidate in candidates
    )


def select_technologies(
    request: TechnologyRequest,
    registry: TowerRegistry | None = None,
) -> dict:
    """Select an executable set that covers every required mission capability."""
    registry = registry or load_registry()
    mission_id = request.mission_id.strip()
    if not mission_id:
        raise ValueError("mission_id must be a non-empty string")
    minimum_name = request.minimum_proof_class or "illustrative"
    if minimum_name not in _PROOF_ORDER:
        raise ValueError(f"unknown minimum proof class: {minimum_name}")
    minimum = _PROOF_ORDER[minimum_name]
    required = {value.casefold().strip() for value in request.capabilities if value.strip()}
    preferred_interfaces = {value.casefold().strip() for value in request.interfaces if value.strip()}

    ranked: list[tuple[int, dict, list[str], set[str]]] = []
    gated_candidates: dict[str, str] = {}
    for row in registry.technologies:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            continue
        proof_name = row.get("proof_class")
        if proof_name not in _PROOF_ORDER:
            raise ValueError(f"technology {row['id']} has unknown proof class: {proof_name}")
        proof = _PROOF_ORDER[proof_name]
        if proof < minimum:
            continue
        tokens = _tokens(row)
        capability_hits = {value for value in required if _capability_matches(value, tokens)}
        interfaces = {item.casefold() for item in row.get("interfaces", []) if isinstance(item, str)}
        interface_hits = preferred_interfaces & interfaces
        if not capability_hits and not interface_hits:
            continue
        if row.get("evidence_state") in _GATED_STATES:
            gated_candidates[row["id"]] = str(row.get("evidence_state"))
            continue
        score = len(capability_hits) * 10 + len(interface_hits) * 4 + proof
        reasons = [f"capability:{value}" for value in sorted(capability_hits)]
        reasons += [f"interface:{value}" for value in sorted(interface_hits)]
        ranked.append((score, row, reasons, capability_hits))

    ranked.sort(key=lambda item: (-item[0], item[1]["id"]))
    selected: list[tuple[int, dict, list[str], set[str]]] = []
    uncovered = set(required)
    remaining = list(ranked)
    while uncovered and remaining:
        remaining.sort(
            key=lambda item: (
                -len(item[3] & uncovered),
                -item[0],
                item[1]["id"],
            )
        )
        candidate = remaining.pop(0)
        if not (candidate[3] & uncovered):
            break
        selected.append(candidate)
        uncovered -= candidate[3]
    if not uncovered:
        for candidate in ranked:
            if len(selected) >= 5:
                break
            if candidate in selected:
                continue
            if any(reason.startswith("interface:") for reason in candidate[2]):
                selected.append(candidate)

    registry_sha = hashlib.sha256(registry.canonical_bytes()).hexdigest()
    agents = sorted({
        agent
        for _, row, _, _ in selected
        for agent in row.get("megamind", {}).get("agents", [])
        if isinstance(agent, str)
    })
    pistons = sorted({
        piston
        for _, row, _, _ in selected
        for piston in row.get("megamind", {}).get("pistons", [])
        if isinstance(piston, str)
    })
    return {
        "mission_id": mission_id,
        "technology_ids": [row["id"] for _, row, _, _ in selected] if not uncovered else [],
        "agent_ids": agents if not uncovered else [],
        "piston_ids": pistons if not uncovered else [],
        "reasons": {row["id"]: reasons for _, row, reasons, _ in selected} if not uncovered else {},
        "required_capabilities": sorted(required),
        "unmatched_capabilities": sorted(uncovered),
        "gated_candidates": dict(sorted(gated_candidates.items())),
        "tower_registry_sha256": registry_sha,
    }
