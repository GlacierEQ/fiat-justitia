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
    assert payload["manifest_commit"] == "a40257552962d0829a2f388d3c4f49296e49b78d"
    assert payload["manifest_sha256"] == "4cdd5e4744a772a503b3189272294478cbdc5bc852599f0c8254f12475e9a9d1"
