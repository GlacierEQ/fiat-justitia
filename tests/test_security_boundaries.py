"""Executable regression tests for Tower trust and process boundaries."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tower import build, integrity
from tower.proofs import build_proof_report
from tower.registry import TowerRegistry


class SecurityBoundaryTests(unittest.TestCase):
    def test_integrity_ignores_absolute_ancestor_names(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "build" / "checkout"
            governed = root / "src" / "governed.py"
            governed.parent.mkdir(parents=True)
            governed.write_text("print('governed')\n", encoding="utf-8")
            with patch.object(integrity, "REPO_ROOT", root):
                self.assertTrue(integrity._eligible(governed))

    def test_integrity_rejects_files_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "checkout"
            root.mkdir()
            outside = Path(temporary) / "outside.py"
            outside.write_text("print('outside')\n", encoding="utf-8")
            with patch.object(integrity, "REPO_ROOT", root):
                self.assertFalse(integrity._eligible(outside))

    def test_command_policy_rejects_shells_and_traversal(self) -> None:
        self.assertIn("forbidden", build._validate_argv(["bash", "-lc", "echo unsafe"]).lower())
        self.assertIn("escapes", build._validate_argv(["../outside-tool"]).lower())
        self.assertIsNone(build._validate_argv(["python3", "-m", "compileall", "src"]))
        self.assertIsNone(build._validate_argv(["build/generated-test-binary"]))

    def test_command_policy_admits_declared_database_and_hdl_compilers(self) -> None:
        self.assertIsNone(build._validate_argv(["psql", "--version"]))
        self.assertIsNone(build._validate_argv(["ghdl", "--version"]))

    def test_build_floor_rejects_unapproved_primary_tool(self) -> None:
        result = build.build_floor({
            "id": "unsafe",
            "toolchain": {
                "tool": "curl",
                "reference_pin": "1",
                "build": [["curl", "https://example.invalid"]],
                "test": [],
            },
            "execution": {"hardware_gate": "", "ci_tier": "portable"},
        })
        self.assertEqual(result["status"], "INVALID_MANIFEST")

    def test_benchmark_failure_fails_proof_gate(self) -> None:
        technology = {
            "id": "bench",
            "easy_example": "languages/python/easy_fibonacci.py",
            "advanced_example": "languages/python/advanced_async_orchestrator.py",
            "evidence_state": "benchmark",
            "proof_class": "benchmark",
            "primary_evidence": ["https://example.invalid/evidence"],
        }
        source = Path("registry/tower.yml")
        registry = TowerRegistry(
            payload={"tower_id": "test", "technologies": [technology]},
            source=source,
            source_files=(source,),
        )
        report = build_proof_report(
            registry,
            {"results": [{"technology_id": "bench", "status": "VERIFIED"}]},
            {"results": [{"technology_id": "bench", "status": "FAILED_TIMEOUT"}]},
        )
        self.assertEqual(report["floors"][0]["proof_status"], "FAILED")

    def test_generated_facade_contains_validation_gate(self) -> None:
        source = Path("src/babel_registry.py").read_text(encoding="utf-8")
        self.assertIn("_validated_registry", source)
        self.assertIn("validate_registry", source)


if __name__ == "__main__":
    unittest.main()
