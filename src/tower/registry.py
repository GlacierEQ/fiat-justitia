"""Canonical Tower registry loader.

``registry/tower.yml`` is the root authority. It references contained technology
fragments and one contained advanced-claim contract fragment. Together they form
one canonical registry, one deterministic identity, and one receipt boundary.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_REGISTRY = REPO_ROOT / "registry" / "tower.yml"
PACKAGED_REGISTRY = Path(__file__).resolve().parent / "data" / "tower.yml"
DEFAULT_REGISTRY = REPOSITORY_REGISTRY if REPOSITORY_REGISTRY.is_file() else PACKAGED_REGISTRY

_REQUIRED_TECH_FIELDS = {
    "id", "name", "evidence_state", "proof_class",
}
_REQUIRED_CLAIM_FIELDS = {
    "signature_innovation",
    "proof_surface",
    "required_source_patterns",
    "expected_failure_cases",
    "required_receipt_fields",
    "forbidden_claim_patterns",
}


@dataclass(frozen=True)
class TowerRegistry:
    payload: dict[str, Any]
    source: Path
    source_files: tuple[Path, ...]

    @property
    def technologies(self) -> list[dict[str, Any]]:
        rows = self.payload.get("technologies", [])
        return list(rows) if isinstance(rows, list) else []

    @property
    def claim_contracts(self) -> dict[str, dict[str, Any]]:
        rows = self.payload.get("claim_contracts", {})
        return dict(rows) if isinstance(rows, dict) else {}

    @property
    def claim_contract_metadata(self) -> dict[str, Any]:
        value = self.payload.get("claim_contract_metadata", {})
        return dict(value) if isinstance(value, dict) else {}

    @property
    def fragment_files(self) -> tuple[Path, ...]:
        return tuple(path for path in self.source_files if path != self.source)

    def canonical_bytes(self) -> bytes:
        """Serialize the complete merged registry for identity and receipts."""
        return json.dumps(
            self.payload,
            separators=(",", ":"),
            sort_keys=True,
            ensure_ascii=False,
        ).encode("utf-8")

    def by_id(self, technology_id: str) -> dict[str, Any] | None:
        """Return a case-insensitive ID/name match without trusting malformed rows."""
        key = technology_id.casefold()
        for row in self.technologies:
            if not isinstance(row, dict):
                continue
            row_id = row.get("id")
            row_name = row.get("name")
            if (isinstance(row_id, str) and row_id.casefold() == key) or (
                isinstance(row_name, str) and row_name.casefold() == key
            ):
                return row
        return None

    def claim_contract_for(self, technology_id: str) -> dict[str, Any] | None:
        key = technology_id.casefold()
        for contract_id, contract in self.claim_contracts.items():
            if isinstance(contract_id, str) and contract_id.casefold() == key and isinstance(contract, dict):
                return dict(contract)
        return None

    def iter_interfaces(self) -> Iterable[tuple[str, str]]:
        for row in self.technologies:
            if not isinstance(row, dict) or not isinstance(row.get("id"), str):
                continue
            interfaces = row.get("interfaces", [])
            if not isinstance(interfaces, list):
                continue
            for interface in interfaces:
                if isinstance(interface, str):
                    yield row["id"], interface


def _read_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"{label} not found: {path}") from exc
    except OSError as exc:
        raise ValueError(f"{label} cannot be read: {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is not valid JSON-compatible YAML: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} root must be an object: {path}")
    return payload


def _contained_fragment(index: Path, relative: str) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError(f"Tower fragment must stay inside registry root: {relative}")
    root = index.parent.resolve()
    candidate = (root / rel).resolve(strict=False)
    try:
        candidate.relative_to(root)
    except ValueError:
        raise ValueError(f"Tower fragment escapes registry root: {relative}") from None
    if candidate == root:
        raise ValueError(f"Tower fragment must name a file below registry root: {relative}")
    return candidate


def load_registry(path: Path | str | None = None) -> TowerRegistry:
    source = Path(path).resolve() if path is not None else DEFAULT_REGISTRY.resolve()
    index = _read_object(source, "Tower registry")
    fragments = index.get("fragments", [])
    inline = index.get("technologies", [])
    source_files: list[Path] = [source]

    if not isinstance(fragments, list) or not all(isinstance(item, str) for item in fragments):
        raise ValueError("Tower registry fragments must be a list of relative paths")
    if not isinstance(inline, list):
        raise ValueError("Tower registry technologies must be a list")

    if fragments:
        if inline:
            raise ValueError("Tower registry cannot mix inline technologies and fragments")
        technologies: list[dict[str, Any]] = []
        seen: set[str] = set()
        for relative in fragments:
            fragment_path = _contained_fragment(source, relative)
            fragment = _read_object(fragment_path, "Tower registry fragment")
            rows = fragment.get("technologies")
            if rows is None:
                rows = fragment.get("documents")
            if rows is None:
                rows = fragment.get("pistons")
            if isinstance(rows, dict):
                rows = list(rows.values())
            if not isinstance(rows, list):
                raise ValueError(f"Tower fragment technologies must be a list: {relative}")
            for row in rows:
                if not isinstance(row, dict):
                    raise ValueError(f"Tower fragment record must be an object: {relative}")
                technology_id = row.get("id")
                if isinstance(technology_id, str):
                    normalized_id = technology_id.casefold()
                    if normalized_id in seen:
                        raise ValueError(f"duplicate technology id across fragments: {technology_id}")
                    seen.add(normalized_id)
                technologies.append(row)
            source_files.append(fragment_path)
        payload: dict[str, Any] = {**index, "technologies": technologies}
    else:
        payload = dict(index)

    contract_relative = index.get("claim_contracts")
    if not isinstance(contract_relative, str) or not contract_relative:
        raise ValueError("Tower registry claim_contracts must name a contained contract fragment")
    contract_path = _contained_fragment(source, contract_relative)
    contract_payload = _read_object(contract_path, "Tower advanced claim contracts")
    contracts = contract_payload.get("contracts")
    if not isinstance(contracts, dict):
        raise ValueError("Tower advanced claim contracts must contain a contracts object")
    source_files.append(contract_path)
    payload["claim_contract_source"] = contract_relative
    payload["claim_contracts"] = contracts
    payload["claim_contract_metadata"] = {
        key: value for key, value in contract_payload.items() if key != "contracts"
    }

    return TowerRegistry(
        payload=payload,
        source=source,
        source_files=tuple(source_files),
    )


def _validate_string_list(value: Any, label: str, errors: list[str], *, nonempty: bool = True) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        errors.append(f"{label} must be a list of non-empty strings")
        return []
    if nonempty and not value:
        errors.append(f"{label} must not be empty")
    return value


def validate_registry(registry: TowerRegistry, *, check_paths: bool = True) -> list[str]:
    errors: list[str] = []
    payload = registry.payload
    if payload.get("tower_id") not in {"glaciereq.tower-of-babel.v1", "glaciereq.fiat-justitia.v1"}:
        errors.append("tower_id must be glaciereq.tower-of-babel.v1 or glaciereq.fiat-justitia.v1")
    governance = payload.get("governance")
    if not isinstance(governance, dict):
        errors.append("governance must be an object")
        governance = {}
    if governance.get("canonical_source") != "registry/tower.yml":
        errors.append("governance.canonical_source must be registry/tower.yml")
    fragments = payload.get("fragments", [])
    if not isinstance(fragments, list):
        errors.append("fragments must be a list")
        fragments = []
    if fragments and len(registry.source_files) != len(fragments) + 2:
        errors.append("every declared Tower technology and claim-contract fragment must be loaded")
    technologies = payload.get("technologies")
    if not isinstance(technologies, list) or not technologies:
        return errors + ["technologies must be a non-empty list"]

    ids: set[str] = set()
    names: set[str] = set()
    allowed_states = set(governance.get("evidence_states", []))
    allowed_proofs = set(governance.get("proof_classes", []))
    repository_examples_available = (REPO_ROOT / "languages").is_dir()
    should_check_paths = check_paths and repository_examples_available

    for index, row in enumerate(technologies):
        label = f"technology[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{label} must be an object")
            continue
        req_fields = {"id", "name", "evidence_state", "proof_class"}
        if "extension" in row or "toolchain" in row:
            req_fields = {
                "id", "name", "extension", "category", "artifact_type",
                "what", "where", "when", "why", "how",
                "easy_example", "advanced_example", "evidence_state", "proof_class",
                "toolchain", "execution", "interfaces", "megamind", "primary_evidence",
            }
        missing = sorted(req_fields - set(row))
        if missing:
            errors.append(f"{label} missing fields: {', '.join(missing)}")
            continue
        tech_id = row.get("id")
        name = row.get("name")
        if not isinstance(tech_id, str) or not tech_id.strip():
            errors.append(f"{label}.id must be a non-empty string")
            continue
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{tech_id}.name must be a non-empty string")
            continue
        normalized_id = tech_id.casefold()
        normalized_name = name.casefold()
        if normalized_id in ids:
            errors.append(f"duplicate technology id: {tech_id}")
        ids.add(normalized_id)
        if normalized_name in names:
            errors.append(f"duplicate technology name: {name}")
        names.add(normalized_name)

        for key in ("what", "where", "when", "why", "how"):
            if key in row and (not isinstance(row.get(key), str) or len(row[key].strip()) < 12):
                errors.append(f"{tech_id}.{key} must be a substantive string")
        if row.get("evidence_state") and row.get("evidence_state") not in allowed_states:
            errors.append(f"{tech_id}.evidence_state is not governed")
        if row.get("proof_class") and row.get("proof_class") not in allowed_proofs:
            errors.append(f"{tech_id}.proof_class is not governed")
        if "toolchain" in row:
            toolchain = row.get("toolchain")
            if not isinstance(toolchain, dict) or not isinstance(toolchain.get("tool"), str) or not toolchain.get("tool") or not isinstance(toolchain.get("reference_pin"), str) or not toolchain.get("reference_pin"):
                errors.append(f"{tech_id}.toolchain requires string tool and reference_pin")
        if "execution" in row:
            execution = row.get("execution")
            if not isinstance(execution, dict) or not isinstance(execution.get("ci_tier"), str) or not execution.get("ci_tier"):
                errors.append(f"{tech_id}.execution requires ci_tier")
        if "interfaces" in row:
            interfaces = row.get("interfaces")
            if not isinstance(interfaces, list) or not all(isinstance(item, str) for item in interfaces):
                errors.append(f"{tech_id}.interfaces must be a string list")
        if "megamind" in row:
            ownership = row.get("megamind")
            if not isinstance(ownership, dict) or not isinstance(ownership.get("agents"), list) or not isinstance(ownership.get("pistons"), list):
                errors.append(f"{tech_id}.megamind requires agent and piston lists")
        if "primary_evidence" in row:
            evidence = row.get("primary_evidence")
            if not isinstance(evidence, list) or not evidence:
                errors.append(f"{tech_id}.primary_evidence requires at least one source")
            else:
                for uri in evidence:
                    if not isinstance(uri, str) or not uri.startswith("https://"):
                        errors.append(f"{tech_id}.primary_evidence must contain HTTPS URLs")

        if should_check_paths:
            for key in ("easy_example", "advanced_example"):
                if key in row:
                    value = row.get(key)
                    if not isinstance(value, str) or not value:
                        errors.append(f"{tech_id}.{key} must be a non-empty path")
                        continue
                    if value.startswith("N/A"):
                        continue
                    rel = Path(value)
                    if rel.is_absolute() or ".." in rel.parts:
                        errors.append(f"{tech_id}.{key} must stay inside the repository")
                    elif not (REPO_ROOT / rel).is_file():
                        errors.append(f"{tech_id}.{key} missing: {rel}")

    contracts = registry.claim_contracts
    normalized_contract_ids = {
        key.casefold() for key in contracts if isinstance(key, str)
    }
    tech_contract_ids = {row["id"].casefold() for row in technologies if "advanced_example" in row}
    if tech_contract_ids:
        missing = sorted(tech_contract_ids - normalized_contract_ids)
        if missing:
            errors.append("missing advanced claim contracts: " + ", ".join(missing))

    metadata = registry.claim_contract_metadata
    if metadata.get("authority") != "registry/tower.yml":
        errors.append("advanced claim contract authority must be registry/tower.yml")
    if metadata.get("contract_type") != "advanced_exhibit_semantic_claims":
        errors.append("advanced claim contract type is invalid")
    if not isinstance(metadata.get("global_claim_boundary"), str) or len(metadata["global_claim_boundary"].strip()) < 40:
        errors.append("advanced claim contracts require a substantive global_claim_boundary")

    for contract_id, contract in contracts.items():
        label = f"claim_contract[{contract_id}]"
        if not isinstance(contract_id, str) or not isinstance(contract, dict):
            errors.append(f"{label} must be an object keyed by technology id")
            continue
        missing = sorted(_REQUIRED_CLAIM_FIELDS - set(contract))
        if missing:
            errors.append(f"{label} missing fields: {', '.join(missing)}")
            continue
        for key in ("signature_innovation", "proof_surface"):
            if not isinstance(contract.get(key), str) or len(contract[key].strip()) < 12:
                errors.append(f"{label}.{key} must be a substantive string")
        for key in (
            "required_source_patterns",
            "expected_failure_cases",
            "required_receipt_fields",
            "forbidden_claim_patterns",
        ):
            values = _validate_string_list(contract.get(key), f"{label}.{key}", errors)
            if key.endswith("patterns"):
                for pattern in values:
                    try:
                        re.compile(pattern, re.IGNORECASE)
                    except re.error as exc:
                        errors.append(f"{label}.{key} contains invalid regex {pattern!r}: {exc}")

    return errors
