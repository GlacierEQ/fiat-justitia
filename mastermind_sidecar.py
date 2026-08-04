#!/usr/bin/env python3
"""Tower sidecar: derived telemetry, never hard-coded counts."""
import json
import time

from tower.integrity import verify_integrity
from tower.registry import load_registry


def get_telemetry():
    registry = load_registry()
    integrity = verify_integrity()
    technologies = registry.technologies
    return {
        "repo_name": "the-tower-of-babel",
        "status": "OPERATIONAL" if integrity["ok"] else "DEGRADED",
        "timestamp": time.time(),
        "integrity": integrity,
        "total_technologies": len(technologies),
        "total_exhibits": len(technologies) * 2,
        "evidence_states": sorted({row["evidence_state"] for row in technologies}),
        "version": "1.1.0",
    }


if __name__ == "__main__":
    print(json.dumps(get_telemetry(), indent=2, sort_keys=True))
