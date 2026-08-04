#!/usr/bin/env python3
"""Compatibility facade generated from registry/tower.yml."""
from pathlib import Path
from tower.registry import load_registry, validate_registry


def _validated_registry(repo_root=None):
    if repo_root is not None:
        target = Path(repo_root) / "registry" / "tower.yml"
        registry = load_registry(target)
    else:
        registry = load_registry()
    errors = validate_registry(registry)
    if errors:
        raise RuntimeError("Invalid Tower registry: " + "; ".join(errors))
    return registry


class BabelRegistryEngine:
    def __init__(self, repo_root=None):
        self.registry = _validated_registry(repo_root=repo_root)

    def get_spec(self, lang_key: str):
        row = self.registry.by_id(lang_key)
        if row is None:
            return {"status": "UNKNOWN_SPEC", "ok": False}
        return {**row, "status": "VALIDATED_W4H_SPEC", "ok": True}


_REGISTRY = _validated_registry()
BABEL_REGISTRY = {row["id"]: row for row in _REGISTRY.technologies}


if __name__ == "__main__":
    print(f"Tower of Babel Registry Initialized: {len(_REGISTRY.technologies)} Technologies Registered.")
