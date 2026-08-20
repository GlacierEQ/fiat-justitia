#!/usr/bin/env python3
"""Validate fiat-justitia factual APEX bindings and Operator authority."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / ".glaciereq" / "nervous-system.node.json"
README_PATH = ROOT / "README.md"
APEX_URL = "https://raw.githubusercontent.com/GlacierEQ/AKOS/main/governance/glaciereq.nervous-system.v2.json"
USER_AGENT = "GlacierEQ-fiat-justitia-APEX-validator/2.1"
REQUIRED_AUTHORITY = {
    "authority_holder": "OPERATOR",
    "operator_project_direction_authority": True,
    "machine_project_direction_authority": False,
    "machine_asset_disposition_authority": False,
    "machine_estate_hierarchy_authority": False,
    "historical_receipt_creates_current_authority": False,
}


def _read_json(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} cannot be loaded: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} root must be an object")
    return value


def _fetch_manifest() -> tuple[dict, str]:
    request = Request(APEX_URL, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=20) as response:
            body = response.read()
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"APEX manifest unavailable: {exc}") from exc
    value = json.loads(body.decode("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("APEX manifest root must be an object")
    return value, hashlib.sha256(body).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freshness", action="store_true", help="Emit current APEX manifest digest for external comparison.")
    args = parser.parse_args()

    errors: list[str] = []
    notices: list[str] = []
    try:
        contract = _read_json(CONTRACT_PATH, "local nervous-system contract")
        manifest, manifest_sha256 = _fetch_manifest()
    except (ValueError, RuntimeError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1

    repository = os.environ.get("GITHUB_REPOSITORY", contract.get("repository", ""))
    node = manifest.get("nodes", {}).get(repository)
    apex = manifest.get("apex_logic", {})
    authority = manifest.get("operator_authority", {})

    if manifest.get("schema_id") != "glaciereq.nervous-system.v2":
        errors.append("APEX nervous-system schema drift")
    for field, expected in REQUIRED_AUTHORITY.items():
        if authority.get(field) != expected:
            errors.append(f"Operator authority invariant drift: {field}")
    if apex.get("selection_scope") != "OPERATOR_AUTHORIZED_EXECUTION_OPTIONS_ONLY":
        errors.append("execution selection scope drift")
    if apex.get("selection_confers_project_authority") is not False:
        errors.append("execution selection must not confer project authority")
    if apex.get("operator_objective_precedence") is not True:
        errors.append("Operator objective precedence drift")

    expected = {
        "schema_id": "glaciereq.nervous-system-node.v2",
        "nervous_system_schema_id": manifest.get("schema_id"),
        "repository": repository,
        "apex_manifest": APEX_URL,
        "selection_scope": "OPERATOR_AUTHORIZED_EXECUTION_OPTIONS_ONLY",
        "selection_confers_project_authority": False,
        "challengeable": True,
        "capability_donor_preservation": True,
        "operating_sequence": manifest.get("operating_sequence"),
    }
    for field, value in expected.items():
        if contract.get(field) != value:
            errors.append(f"factual contract drift: {field}")

    contract_authority = contract.get("operator_authority", {})
    for field, expected_value in REQUIRED_AUTHORITY.items():
        if contract_authority.get(field) != expected_value:
            errors.append(f"local Operator authority invariant drift: {field}")

    strict_topology = os.getenv("APEX_OPERATOR_ENFORCE_DESCRIPTIVE_TOPOLOGY") == "1"
    if not isinstance(node, dict):
        notices.append(f"{repository} is absent from the descriptive capability map; no hierarchy or disposition inference follows")
    else:
        if contract.get("role") != node.get("role"):
            notices.append("descriptive role differs from capability map")
        if contract.get("apex_role") != node.get("apex_role"):
            notices.append("descriptive apex_role differs from capability map")
        readme = README_PATH.read_text(encoding="utf-8").lower()
        for term in node.get("required_terms", []):
            if str(term).lower() not in readme:
                message = f"README missing descriptive capability term: {term}"
                (errors if strict_topology else notices).append(message)
        for link in node.get("required_links", []):
            if str(link).lower() not in readme:
                message = f"README missing interoperability link: {link}"
                (errors if strict_topology else notices).append(message)

    for notice in notices:
        print(f"::notice::{notice}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"::error::{error}", file=sys.stderr)
        return 1

    result = {
        "schema": "glaciereq.nervous-system.validation.v2.1",
        "status": "verified",
        "repository": repository,
        "role": contract.get("role"),
        "apex_role": contract.get("apex_role"),
        "role_semantics": "DESCRIPTIVE_CAPABILITY_METADATA_ONLY",
        "selection_mode": apex.get("selection_mode"),
        "selection_scope": apex.get("selection_scope"),
        "selection_confers_project_authority": False,
        "operator_authority": "VERIFIED",
        "machine_project_authority": False,
        "descriptive_topology_enforced": strict_topology,
        "manifest_version": manifest.get("version"),
        "manifest_sha256": manifest_sha256,
        "source": "current_apex_mesh",
        "notices": notices,
    }
    if args.freshness:
        result["freshness"] = "current_fetch"
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
