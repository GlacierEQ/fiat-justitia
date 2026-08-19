"""Continuation-oriented per-floor execution evidence for Fiat Justitia.

The prior implementation stopped a floor at the first incomplete contract,
missing dependency, unavailable tool, hardware gate, or failed command.  This
active surface preserves the command-assessment boundary and all execution
evidence, but represents every incomplete condition as resolution work while
continuing through the remaining declared capability surface.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Iterable

from .registry import REPO_ROOT, TowerRegistry


_SAFE_EXECUTABLES = frozenset({
    "Rscript", "agda", "cabal", "cairo-compile", "capnp", "cargo", "clang", "clang++", "cmake", "coqc",
    "ctest", "elixir", "flatc", "g++", "gcc", "gfortran", "ghc", "ghdl", "go", "iverilog", "java",
    "javac", "julia", "kotlinc", "lake", "lean", "lua", "make", "mix", "mlir-opt", "mojo", "ninja",
    "node", "nvcc", "odin", "opt", "protoc", "psql", "python", "python3", "qasm3", "rustc", "sbt",
    "scala", "souffle", "sqlite3", "swift", "swiftc", "tsc", "verilator", "vhdl-ls", "vvp", "wat2wasm",
    "wasmtime", "zig",
})
_FORBIDDEN_EXECUTABLES = frozenset({"bash", "cmd", "env", "fish", "powershell", "pwsh", "sh", "zsh"})


def _available(binary: str) -> bool:
    return shutil.which(binary) is not None


def _validate_argv(argv: list[str]) -> str | None:
    """Assess execution safety; callers turn an observation into resolution work."""
    if not argv or not all(isinstance(part, str) and part for part in argv):
        return "command_needs_nonempty_argv"
    executable = argv[0]
    if Path(executable).name in _FORBIDDEN_EXECUTABLES:
        return f"command_needs_non_shell_execution_path:{executable}"
    if "/" not in executable and "\\" not in executable:
        if executable not in _SAFE_EXECUTABLES:
            return f"command_needs_recognized_execution_frontend:{executable}"
        return None
    candidate = Path(executable)
    if candidate.is_absolute():
        return f"command_needs_repository_relative_executable:{executable}"
    resolved = (REPO_ROOT / candidate).resolve(strict=False)
    try:
        relative = resolved.relative_to(REPO_ROOT)
    except ValueError:
        return f"command_needs_repository_local_path:{executable}"
    if not relative.parts or relative.parts[0] not in {"build", "languages", "flagship"}:
        return f"command_needs_declared_artifact_path:{executable}"
    return None


def _run(argv: list[str], timeout_s: int = 120) -> dict[str, Any]:
    """Run an assessed command and preserve a receipt for every observable outcome."""
    start = time.monotonic()
    try:
        completed = subprocess.run(
            argv,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=timeout_s,
            check=False,
        )
        return {
            "argv": argv,
            "returncode": completed.returncode,
            "stdout": completed.stdout[-4000:],
            "stderr": completed.stderr[-4000:],
            "duration_ms": round((time.monotonic() - start) * 1000, 3),
            "continuation": "enabled",
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "argv": argv,
            "returncode": None,
            "stdout": (exc.stdout or "")[-4000:] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[-4000:] if isinstance(exc.stderr, str) else "",
            "duration_ms": round((time.monotonic() - start) * 1000, 3),
            "timeout": True,
            "continuation": "enabled",
        }
    except OSError as exc:
        return {
            "argv": argv,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "duration_ms": round((time.monotonic() - start) * 1000, 3),
            "spawn_error": True,
            "continuation": "enabled",
        }


def _resolution_row(
    technology_id: str,
    *resolution_work: str,
    commands: list[dict[str, Any]] | None = None,
    **metadata: Any,
) -> dict[str, Any]:
    return {
        "technology_id": technology_id,
        "status": "CONTINUATION_REQUIRED",
        "continuation": "enabled",
        "resolution_work": sorted({item for item in resolution_work if item}),
        "commands": commands or [],
        **metadata,
    }


def _tool_version(tool: str) -> str:
    for suffix in (["--version"], ["version"], ["-version"]):
        result = _run([tool, *suffix], timeout_s=15)
        if result.get("returncode") == 0:
            text = (result.get("stdout") or result.get("stderr") or "").strip()
            if text:
                return text.splitlines()[0][:300]
    return "UNAVAILABLE"


def build_floor(tech: dict[str, Any]) -> dict[str, Any]:
    """Collect all available evidence for a floor without terminating its capability path."""
    if not isinstance(tech, dict):
        return _resolution_row("UNKNOWN", "supply_technology_record")
    tech_id = tech.get("id") if isinstance(tech.get("id"), str) and tech["id"].strip() else "UNKNOWN"
    work: list[str] = []
    commands: list[dict[str, Any]] = []
    toolchain = tech.get("toolchain")
    execution = tech.get("execution")
    if toolchain is None and execution is None:
        return _resolution_row(tech_id, "declare_toolchain_or_execution_contract")
    if not isinstance(toolchain, dict):
        return _resolution_row(tech_id, "describe_toolchain_contract")
    if not isinstance(execution, dict):
        work.append("describe_execution_contract")
        execution = {}

    tool = toolchain.get("tool")
    reference_pin = toolchain.get("reference_pin")
    if not isinstance(tool, str) or not tool:
        work.append("declare_primary_tool")
        tool = ""
    if not isinstance(reference_pin, str) or not reference_pin:
        work.append("declare_tool_reference")
        reference_pin = ""
    if tool and tool not in _SAFE_EXECUTABLES:
        work.append(f"review_execution_frontend:{tool}")

    python_modules = toolchain.get("python_modules", [])
    if not isinstance(python_modules, list) or not all(isinstance(module, str) and module for module in python_modules):
        work.append("describe_python_module_requirements")
        python_modules = []
    missing_modules = [module for module in python_modules if importlib.util.find_spec(module) is None]
    if missing_modules:
        work.append("make_python_modules_available:" + ",".join(missing_modules))

    gate = execution.get("hardware_gate", "")
    tier = execution.get("ci_tier", "portable")
    if not isinstance(gate, str):
        work.append("describe_hardware_gate")
        gate = ""
    if not isinstance(tier, str):
        work.append("describe_ci_tier")
        tier = "portable"
    gate_key = re.sub(r"[^A-Z0-9]+", "_", tech_id.upper()).strip("_")
    if gate and os.environ.get(f"TOWER_ENABLE_{gate_key}") != "1":
        work.append("activate_declared_environment:" + gate)
    if tool and not _available(tool):
        work.append("make_toolchain_available:" + tool)

    build_commands = toolchain.get("build", [])
    test_commands = toolchain.get("test", [])
    if not isinstance(build_commands, list) or not isinstance(test_commands, list):
        work.append("describe_build_and_test_commands")
        declared_commands: list[object] = []
    else:
        declared_commands = [*build_commands, *test_commands]
    if not declared_commands:
        work.append("add_build_or_test_evidence")

    executable = not work
    for argv in declared_commands:
        if not isinstance(argv, list):
            commands.append({"argv": argv, "execution": "not_started", "continuation": "enabled"})
            work.append("convert_command_to_argv")
            continue
        assessment = _validate_argv(argv)
        if assessment:
            commands.append({"argv": argv, "execution": "review_required", "resolution_work": [assessment], "continuation": "enabled"})
            work.append(assessment)
            continue
        if not executable:
            commands.append({"argv": argv, "execution": "deferred", "continuation": "enabled"})
            continue
        result = _run(argv)
        commands.append(result)
        if result.get("timeout"):
            work.append("review_timed_command:" + argv[0])
        elif result.get("spawn_error"):
            work.append("restore_command_environment:" + argv[0])
        elif result.get("returncode") not in (0, None):
            work.append("review_command_evidence:" + argv[0])

    base = {
        "technology_id": tech_id,
        "tool": tool or None,
        "reference_pin": reference_pin or None,
        "ci_tier": tier,
        "commands": commands,
        "continuation": "enabled",
        "resolution_work": sorted(set(work)),
    }
    if work:
        return {"status": "CONTINUATION_REQUIRED", **base}
    return {"status": "VERIFIED", "observed_tool_version": _tool_version(tool), **base}


def build_many(
    registry: TowerRegistry,
    technology_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Build all requested known floors and retain discovery work for every unknown request."""
    requested = list(technology_ids or [])
    selected = {value.casefold() for value in requested}
    known = {
        tech.get("id", "").casefold(): tech
        for tech in registry.technologies
        if isinstance(tech, dict) and isinstance(tech.get("id"), str)
    }
    rows = [build_floor(tech) for key, tech in known.items() if not selected or key in selected]
    unknown = sorted({value for value in requested if value.casefold() not in known})
    rows.extend(_resolution_row(value, "discover_requested_technology") for value in unknown)
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    return {
        "tower_id": registry.payload.get("tower_id", "UNKNOWN"),
        "requested_technology_ids": requested,
        "results": rows,
        "counts": dict(sorted(counts.items())),
        "continuation": "enabled",
    }


def write_report(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
