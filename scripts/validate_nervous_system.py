#!/usr/bin/env python3
"""Validate Tower's pinned GlacierEQ nervous-system contract."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / ".glaciereq" / "nervous-system.node.json"
README_PATH = ROOT / "README.md"
RAW_BASE = "https://raw.githubusercontent.com"
USER_AGENT = "GlacierEQ-Tower-Nervous-System-Validator/1.0"


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"{label} not found: {path}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} cannot be loaded: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} root must be an object")
    return payload


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _fetch(url: str, attempts: int = 3, timeout: int = 20) -> bytes:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=timeout) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(1.0 * (attempt + 1))
    raise RuntimeError(f"unable to fetch {url}: {last_error}")


def _validate(
    contract: dict[str, Any],
    manifest: dict[str, Any],
    repository: str,
) -> list[str]:
    errors: list[str] = []
    node = manifest.get("nodes", {}).get(repository)
    if not isinstance(node, dict):
        return [f"{repository} is not registered"]

    if contract.get("schema_id") != manifest.get("schema_id"):
        errors.append("schema_id drift")
    if contract.get("repository") != repository:
        errors.append("repository identity drift")
    if contract.get("role") != node.get("role"):
        errors.append("role drift")

    canonical_repository = manifest.get("canonical_repository")
    canonical_path = manifest.get("canonical_path")
    expected_pointer = f"{canonical_repository}/{canonical_path}"
    if contract.get("canonical_manifest") != expected_pointer:
        errors.append("canonical manifest pointer drift")
    if contract.get("accepted_manifest_version") != manifest.get("version"):
        errors.append("accepted manifest version drift")
    if contract.get("operating_sequence") != manifest.get("operating_sequence"):
        errors.append("operating sequence drift")

    readme = README_PATH.read_text(encoding="utf-8").lower()
    for term in node.get("required_terms", []):
        if not isinstance(term, str) or term.lower() not in readme:
            errors.append(f"README missing term: {term}")
    for link in node.get("required_links", []):
        if not isinstance(link, str) or link.lower() not in readme:
            errors.append(f"README missing link: {link}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verify-remote",
        action="store_true",
        help="Best-effort comparison with the immutable pinned AKOS commit.",
    )
    parser.add_argument(
        "--freshness",
        action="store_true",
        help="Best-effort comparison with AKOS main; drift is reported, not admitted automatically.",
    )
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    contract = _read_json(CONTRACT_PATH, "local nervous-system contract")

    snapshot_value = contract.get("canonical_manifest_snapshot")
    if not isinstance(snapshot_value, str) or not snapshot_value:
        errors.append("canonical_manifest_snapshot must be a repository-relative path")
        snapshot_path = ROOT / "__missing_snapshot__"
    else:
        relative = Path(snapshot_value)
        if relative.is_absolute() or ".." in relative.parts:
            errors.append("canonical_manifest_snapshot escapes repository")
            snapshot_path = ROOT / "__invalid_snapshot__"
        else:
            snapshot_path = ROOT / relative

    try:
        snapshot_bytes = snapshot_path.read_bytes()
    except OSError as exc:
        errors.append(f"pinned manifest snapshot cannot be read: {exc}")
        snapshot_bytes = b""

    expected_sha = contract.get("canonical_manifest_sha256")
    observed_sha = _sha256(snapshot_bytes) if snapshot_bytes else ""
    if not isinstance(expected_sha, str) or len(expected_sha) != 64:
        errors.append("canonical_manifest_sha256 must be a SHA-256 digest")
    elif observed_sha != expected_sha:
        errors.append(
            f"pinned manifest snapshot digest drift: expected {expected_sha}, observed {observed_sha}"
        )

    try:
        manifest = json.loads(snapshot_bytes.decode("utf-8")) if snapshot_bytes else {}
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"pinned manifest snapshot is invalid JSON: {exc}")
        manifest = {}

    repository = os.environ.get("GITHUB_REPOSITORY", contract.get("repository", ""))
    if not isinstance(repository, str) or not repository:
        errors.append("repository identity is missing")
    elif isinstance(manifest, dict):
        errors.extend(_validate(contract, manifest, repository))

    canonical_repository = manifest.get("canonical_repository", "GlacierEQ/AKOS")
    canonical_path = manifest.get(
        "canonical_path", "governance/glaciereq.nervous-system.v1.json"
    )
    pinned_commit = contract.get("canonical_manifest_commit")

    remote_status = "not_requested"
    if args.verify_remote:
        if not isinstance(pinned_commit, str) or len(pinned_commit) != 40:
            errors.append("canonical_manifest_commit must be a full commit SHA")
        else:
            pinned_url = f"{RAW_BASE}/{canonical_repository}/{pinned_commit}/{canonical_path}"
            try:
                remote_bytes = _fetch(pinned_url)
            except RuntimeError as exc:
                warnings.append(f"immutable remote verification unavailable: {exc}")
                remote_status = "unavailable"
            else:
                remote_sha = _sha256(remote_bytes)
                if remote_sha != expected_sha:
                    errors.append(
                        f"immutable AKOS manifest digest mismatch: expected {expected_sha}, observed {remote_sha}"
                    )
                    remote_status = "mismatch"
                else:
                    remote_status = "verified"

    freshness_status = "not_requested"
    if args.freshness:
        latest_url = f"{RAW_BASE}/{canonical_repository}/main/{canonical_path}"
        try:
            latest_bytes = _fetch(latest_url)
        except RuntimeError as exc:
            warnings.append(f"AKOS main freshness check unavailable: {exc}")
            freshness_status = "unavailable"
        else:
            latest_sha = _sha256(latest_bytes)
            if latest_sha == expected_sha:
                freshness_status = "current"
            else:
                freshness_status = "drift"
                warnings.append(
                    f"AKOS main differs from pinned authority: pinned={expected_sha} latest={latest_sha}"
                )

    for warning in warnings:
        print(f"::warning::{warning}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"::error::{error}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "schema": "glaciereq.nervous-system.validation.v2",
                "status": "verified",
                "repository": repository,
                "role": manifest["nodes"][repository]["role"],
                "manifest_version": manifest["version"],
                "manifest_commit": pinned_commit,
                "manifest_sha256": expected_sha,
                "source": "pinned_snapshot",
                "remote_status": remote_status,
                "freshness_status": freshness_status,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
