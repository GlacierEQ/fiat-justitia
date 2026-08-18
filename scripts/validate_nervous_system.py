#!/usr/bin/env python3
"""Validate fiat-justitia against the current APEX nervous-system v2 mesh."""
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
USER_AGENT = "GlacierEQ-fiat-justitia-APEX-validator/2.0"


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
    try:
        contract = _read_json(CONTRACT_PATH, "local nervous-system contract")
        manifest, manifest_sha256 = _fetch_manifest()
    except (ValueError, RuntimeError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1

    repository = os.environ.get("GITHUB_REPOSITORY", contract.get("repository", ""))
    node = manifest.get("nodes", {}).get(repository)
    apex = manifest.get("apex_logic", {})

    if manifest.get("schema_id") != "glaciereq.nervous-system.v2":
        errors.append("APEX nervous-system schema drift")
    if apex.get("selection_mode") != "CURRENT_BEST_REVISABLE":
        errors.append("selection mode drift")
    if apex.get("challengeable") is not True:
        errors.append("mesh selections must remain challengeable")
    if apex.get("capability_donor_preservation") is not True:
        errors.append("capability donor preservation drift")
    if apex.get("operator_objective_precedence") is not True:
        errors.append("operator objective precedence drift")

    if not isinstance(node, dict):
        errors.append(f"{repository} is not registered")
    else:
        expected = {
            "schema_id": "glaciereq.nervous-system-node.v2",
            "nervous_system_schema_id": manifest.get("schema_id"),
            "repository": repository,
            "role": node.get("role"),
            "apex_role": node.get("apex_role"),
            "apex_manifest": APEX_URL,
            "selection_mode": apex.get("selection_mode"),
            "challengeable": True,
            "capability_donor_preservation": True,
            "operating_sequence": manifest.get("operating_sequence"),
        }
        for field, value in expected.items():
            if contract.get(field) != value:
                errors.append(f"{field} drift")

        readme = README_PATH.read_text(encoding="utf-8").lower()
        for term in node.get("required_terms", []):
            if str(term).lower() not in readme:
                errors.append(f"README missing term: {term}")
        for link in node.get("required_links", []):
            if str(link).lower() not in readme:
                errors.append(f"README missing link: {link}")

    if errors:
        for error in errors:
            print(f"::error::{error}", file=sys.stderr)
        return 1

    result = {
        "schema": "glaciereq.nervous-system.validation.v2",
        "status": "verified",
        "repository": repository,
        "role": node["role"],
        "apex_role": node["apex_role"],
        "selection_mode": apex["selection_mode"],
        "manifest_version": manifest["version"],
        "manifest_sha256": manifest_sha256,
        "source": "current_apex_mesh",
    }
    if args.freshness:
        result["freshness"] = "current_fetch"
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
