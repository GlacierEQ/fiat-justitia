#!/usr/bin/env python3
"""Integrity watchdog backed by the real Tower hash engine."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from tower.integrity import verify_integrity


def check_integrity():
    return verify_integrity()


if __name__ == "__main__":
    result = check_integrity()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["ok"] else 1)
