#!/usr/bin/env python3
"""Create or update the repository main-protection ruleset from policy-as-code."""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = REPO_ROOT / "governance" / "main-ruleset.required.json"
DEFAULT_REPOSITORY = "GlacierEQ/the-tower-of-babel"
API_VERSION = "2022-11-28"


def request_json(url: str, token: str, *, method: str = "GET", payload: dict[str, Any] | None = None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "tower-main-ruleset-installer/1.0",
        "X-GitHub-Api-Version": API_VERSION,
    }
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, headers=headers, method=method, data=data)
    with urllib.request.urlopen(request, timeout=20) as response:
        body = response.read()
        return json.loads(body) if body else {}


def install(repository: str, contract_path: Path, token: str) -> dict[str, Any]:
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    payload = {key: value for key, value in contract.items() if key != "tower_metadata"}
    base_url = f"https://api.github.com/repos/{repository}/rulesets"
    existing = request_json(base_url, token)
    target_id = None
    if isinstance(existing, list):
        for ruleset in existing:
            if isinstance(ruleset, dict) and ruleset.get("name") == payload["name"]:
                target_id = ruleset.get("id")
                break
    if isinstance(target_id, int):
        result = request_json(f"{base_url}/{target_id}", token, method="PUT", payload=payload)
        operation = "updated"
    else:
        result = request_json(base_url, token, method="POST", payload=payload)
        operation = "created"
    return {
        "schema": "glaciereq.github-main-ruleset.installation.v1",
        "repository": repository,
        "operation": operation,
        "ruleset_id": result.get("id"),
        "name": result.get("name"),
        "enforcement": result.get("enforcement"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", DEFAULT_REPOSITORY))
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--token", default=os.environ.get("RULESET_ADMIN_TOKEN"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.token:
        raise SystemExit("RULESET_ADMIN_TOKEN is required and must have repository Administration: write.")
    try:
        result = install(args.repository, args.contract.resolve(), args.token)
    except (OSError, ValueError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        raise SystemExit(f"Ruleset installation failed: {exc}") from exc
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
