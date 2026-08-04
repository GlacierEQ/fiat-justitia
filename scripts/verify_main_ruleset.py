#!/usr/bin/env python3
"""Verify GitHub's live main-branch ruleset against the checked-in contract."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = REPO_ROOT / "governance" / "main-ruleset.required.json"
DEFAULT_REPOSITORY = "GlacierEQ/the-tower-of-babel"
API_VERSION = "2022-11-28"


def _request_json(url: str, token: str | None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "tower-main-ruleset-verifier/1.0",
        "X-GitHub-Api-Version": API_VERSION,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.load(response)


def _rule_map(ruleset: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for rule in ruleset.get("rules", []):
        if isinstance(rule, dict) and isinstance(rule.get("type"), str):
            result[rule["type"]] = rule
    return result


def _status_contexts(rule: dict[str, Any]) -> set[str]:
    parameters = rule.get("parameters", {})
    rows = parameters.get("required_status_checks", []) if isinstance(parameters, dict) else []
    return {
        row["context"]
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("context"), str)
    }


def _applies_to_main(ruleset: dict[str, Any]) -> bool:
    conditions = ruleset.get("conditions", {})
    ref_name = conditions.get("ref_name", {}) if isinstance(conditions, dict) else {}
    include = ref_name.get("include", []) if isinstance(ref_name, dict) else []
    return "refs/heads/main" in include or "~DEFAULT_BRANCH" in include


def compare(required: dict[str, Any], live: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if live.get("target") != required.get("target"):
        errors.append(f"target mismatch: expected {required.get('target')!r}, got {live.get('target')!r}")
    if live.get("enforcement") != "active":
        errors.append(f"ruleset enforcement is not active: {live.get('enforcement')!r}")
    if not _applies_to_main(live):
        errors.append("ruleset does not explicitly apply to refs/heads/main or ~DEFAULT_BRANCH")

    required_rules = _rule_map(required)
    live_rules = _rule_map(live)
    for rule_type in required_rules:
        if rule_type not in live_rules:
            errors.append(f"missing required rule: {rule_type}")

    required_status = required_rules.get("required_status_checks")
    live_status = live_rules.get("required_status_checks")
    if required_status and live_status:
        missing = sorted(_status_contexts(required_status) - _status_contexts(live_status))
        if missing:
            errors.append("missing required status contexts: " + ", ".join(missing))
        required_parameters = required_status.get("parameters", {})
        live_parameters = live_status.get("parameters", {})
        if required_parameters.get("strict_required_status_checks_policy") is True and live_parameters.get("strict_required_status_checks_policy") is not True:
            errors.append("strict required-status-check policy is disabled")

    required_pr = required_rules.get("required_pull_request")
    live_pr = live_rules.get("required_pull_request")
    if required_pr and live_pr:
        required_parameters = required_pr.get("parameters", {})
        live_parameters = live_pr.get("parameters", {})
        for key in ("dismiss_stale_reviews_on_push", "required_review_thread_resolution"):
            if required_parameters.get(key) is True and live_parameters.get(key) is not True:
                errors.append(f"pull-request protection {key} is disabled")

    return errors


def verify(repository: str, contract_path: Path, token: str | None) -> dict[str, Any]:
    required = json.loads(contract_path.read_text(encoding="utf-8"))
    base_url = f"https://api.github.com/repos/{repository}/rulesets"
    summaries = _request_json(base_url, token)
    if not isinstance(summaries, list):
        raise ValueError("GitHub rulesets response must be a list")

    candidates: list[dict[str, Any]] = []
    for summary in summaries:
        if not isinstance(summary, dict) or summary.get("target") != "branch":
            continue
        ruleset_id = summary.get("id")
        if not isinstance(ruleset_id, int):
            continue
        full = _request_json(f"{base_url}/{ruleset_id}", token)
        if isinstance(full, dict) and _applies_to_main(full):
            candidates.append(full)

    evaluations = [
        {
            "id": candidate.get("id"),
            "name": candidate.get("name"),
            "errors": compare(required, candidate),
        }
        for candidate in candidates
    ]
    passing = [evaluation for evaluation in evaluations if not evaluation["errors"]]
    return {
        "schema": "glaciereq.github-main-ruleset.verification.v1",
        "repository": repository,
        "contract": str(contract_path.relative_to(REPO_ROOT)),
        "candidate_count": len(candidates),
        "passing_count": len(passing),
        "status": "verified" if passing else "missing_or_nonconforming",
        "evaluations": evaluations,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", DEFAULT_REPOSITORY))
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    parser.add_argument("--advisory", action="store_true", help="Report drift without failing the process.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        result = verify(args.repository, args.contract.resolve(), args.token)
    except (OSError, ValueError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        result = {
            "schema": "glaciereq.github-main-ruleset.verification.v1",
            "repository": args.repository,
            "status": "unavailable",
            "error": str(exc),
        }

    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")

    if result.get("status") == "verified" or args.advisory:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
