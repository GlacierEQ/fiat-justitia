from __future__ import annotations

import json
import subprocess
import sys


def test_pinned_nervous_system_contract_is_reproducible() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/validate_nervous_system.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["status"] == "verified"
    assert payload["source"] == "pinned_snapshot"
    assert payload["manifest_commit"] == "5ef48a8068a8079f3cbca3f83c5800909b1d5239"
    assert payload["manifest_sha256"] == "ce6a7a111a8c134566a1f6542da0fcfcbac110254c5dffb663c2680aeb8a935d"
