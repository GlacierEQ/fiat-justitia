from __future__ import annotations

import subprocess
import sys


def test_advanced_exhibit_contract_and_atlas_are_current() -> None:
    subprocess.run(
        [sys.executable, "tools/audit_advanced_exhibits.py", "--check"],
        check=True,
    )
