"""Honest per-floor toolchain execution with exact blockers."""
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

# Registry commands are data, not ambient authority. Only recognized compiler,
# runtime, schema, proof, and build frontends may be launched from PATH.
_SAFE_EXECUTABLES = frozenset({
    "Rscript",
    "agda",
    "cabal",
    "capnp",
    "cargo",
    "clang",
    "clang++",
    "cmake",
    "coqc",
    "ctest",
    "elixir",
    "flatc",
    "g++",
    "gcc",
    "ghc",
    "ghdl",
    "go",
    "iverilog",
    "julia",
    "lake",
    "lean",
    "make",
    "mix",
    "mlir-opt",
    "mojo",
    "ninja",
    "node",
    "nvcc",
    "odin",
    "opt",
    "protoc",
    "psql",
    "python",
    "python3",
    "rustc",
    "sbt",
    "scala",
    "sqlite3",
    "swift",
    "swiftc",
    "tsc",
    "verilator",
    "vhdl-ls",
    "vvp",
    "wat2wasm",
    "wasmtime",
    "zig",
})
_FORBIDDEN_EXECUTABLES = frozenset({
    "bash",
    "cmd",
    "env",
    "fish",
    "powershell",
    "pwsh",
    "sh",
    "zsh",
})


def _available(binary: str) -> bool:
    return shutil.which(binary) is not None


def _validate_argv(argv: list[str]) -> str | None:
    """Return a blocker when argv exceeds the Tower execution boundary."""
    if not argv or not all(isinstance(part, str) and part for part in argv):
        return "Command must be a non-empty argv string list."
    executable = argv[0]
    if Path(executable).name in _FORBIDDEN_EXECUTABLES:
        return f"Shell and environment wrappers are forbidden: {executable}"
    if "/" not in executable and "\\" not in executable:
        if executable not in _SAFE_EXECUTABLES:
            return f"Executable is not in the governed allowlist: {executable}"
        return None
    candidate = Path(executable)
    if candidate.is_absolute():
        return f"Absolute executable paths are forbidden: {executable}"
    resolved = (REPO_ROOT / candidate).resolve(strict=False)
    try:
        relative = resolved.relative_to(REPO_ROOT)
    except ValueError:
        return f"Executable escapes repository root: {executable}"
    if not relative.parts or relative.parts[0] not in {"build", "languages", "flagship"}:
        return f"Repository executable must live under build/, languages/, or flagship/: {executable}"
    return None


def _run(argv: list[str], timeout_s: int = 120) -> dict[str, Any]:
    """Run a governed argv-only command and return bounded evidence."""
    policy_error = _validate_argv(argv)
    if policy_error:
        return {
            "argv": argv,
            "returncode": None,
            "stdout": "",
            "stderr": policy_error,
            "duration_ms": 0.0,
            "policy_error": True,
        }
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
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "argv": argv,
            "returncode": None,
            "stdout": (exc.stdout or "")[-4000:] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[-4000:] if isinstance(exc.stderr, str) else "",
            "duration_ms": round((time.monotonic() - start) * 1000, 3),
            "timeout": True,
        }
    except OSError as exc:
        return {
            "argv": argv,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "duration_ms": round((time.monotonic() - start) * 1000, 3),
            "spawn_error": True,
        }


def _invalid(technology_id: str, blocker: str, commands: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "technology_id": technology_id,
        "status": "INVALID_MANIFEST",
        "blocker": blocker,
        "commands": commands or [],
    }


def _tool_version(tool: str) -> str:
    """Capture a best-effort observed tool version without calling a shell."""
    for suffix in (["--version"], ["version"], ["-version"]):
        result = _run([tool, *suffix], timeout_s=15)
        if result.get("returncode") == 0:
            text = (result.get("stdout") or result.get("stderr") or "").strip()
            if text:
                return text.splitlines()[0][:300]
    return "UNAVAILABLE"


def build_floor(tech: dict[str, Any]) -> dict[str, Any]:
    """Execute one validated floor, failing closed on incomplete contracts."""
    if not isinstance(tech, dict):
        return _invalid("UNKNOWN", "Technology record must be an object.")
    tech_id = tech.get("id")
    if not isinstance(tech_id, str) or not tech_id.strip():
        return _invalid("UNKNOWN", "Technology id must be a non-empty string.")
    toolchain = tech.get("toolchain")
    execution = tech.get("execution")
    if not isinstance(toolchain, dict):
        return _invalid(tech_id, "toolchain must be an object.")
    if not isinstance(execution, dict):
        return _invalid(tech_id, "execution must be an object.")
    tool = toolchain.get("tool")
    reference_pin = toolchain.get("reference_pin")
    if not isinstance(tool, str) or not tool or not isinstance(reference_pin, str) or not reference_pin:
        return _invalid(tech_id, "toolchain requires string tool and reference_pin.")
    if tool not in _SAFE_EXECUTABLES:
        return _invalid(tech_id, f"Primary tool is not in the governed allowlist: {tool}")

    gate = execution.get("hardware_gate", "")
    tier = execution.get("ci_tier", "portable")
    if not isinstance(gate, str) or not isinstance(tier, str):
        return _invalid(tech_id, "execution gate and ci_tier must be strings.")
    python_modules = toolchain.get("python_modules", [])
    if not isinstance(python_modules, list) or not all(isinstance(module, str) and module for module in python_modules):
        return _invalid(tech_id, "python_modules must be a list of module names.")
    missing_modules = [module for module in python_modules if importlib.util.find_spec(module) is None]
    if missing_modules:
        return {
            "technology_id": tech_id,
            "status": "BLOCKED_DEPENDENCY",
            "blocker": "Required Python module(s) not found: " + ", ".join(missing_modules),
            "tool": tool,
            "reference_pin": reference_pin,
            "commands": [],
        }

    gate_key = re.sub(r"[^A-Z0-9]+", "_", tech_id.upper()).strip("_")
    if gate and os.environ.get(f"TOWER_ENABLE_{gate_key}") != "1":
        status = "BLOCKED_SERVICE" if tier == "service" or "service" in gate.casefold() else "BLOCKED_HARDWARE"
        return {
            "technology_id": tech_id,
            "status": status,
            "blocker": gate,
            "tool": tool,
            "reference_pin": reference_pin,
            "commands": [],
        }
    if not _available(tool):
        return {
            "technology_id": tech_id,
            "status": "BLOCKED_TOOLCHAIN",
            "blocker": f"Required executable not found: {tool}",
            "tool": tool,
            "reference_pin": reference_pin,
            "commands": [],
        }

    build_commands = toolchain.get("build", [])
    test_commands = toolchain.get("test", [])
    if not isinstance(build_commands, list) or not isinstance(test_commands, list):
        return _invalid(tech_id, "Build and test contracts must be lists.")
    declared_commands = build_commands + test_commands
    if not declared_commands:
        return _invalid(tech_id, "At least one build or test command is required for VERIFIED status.")

    (REPO_ROOT / "build").mkdir(exist_ok=True)
    commands: list[dict[str, Any]] = []
    for argv in declared_commands:
        if not isinstance(argv, list):
            return _invalid(tech_id, "Build/test commands must be argv lists.", commands)
        policy_error = _validate_argv(argv)
        if policy_error:
            return _invalid(tech_id, policy_error, commands)
        result = _run(argv)
        commands.append(result)
        if result.get("policy_error"):
            return _invalid(tech_id, str(result.get("stderr", "Command policy rejected argv.")), commands)
        if result.get("spawn_error"):
            return {
                "technology_id": tech_id,
                "status": "BLOCKED_TOOLCHAIN",
                "blocker": f"Command executable could not be started: {argv[0]}: {result.get('stderr', '')}",
                "tool": tool,
                "reference_pin": reference_pin,
                "commands": commands,
            }
        if result.get("returncode") != 0:
            return {
                "technology_id": tech_id,
                "status": "FAILED_TIMEOUT" if result.get("timeout") else "FAILED",
                "blocker": "Command timed out." if result.get("timeout") else "Command failed.",
                "tool": tool,
                "reference_pin": reference_pin,
                "commands": commands,
            }
    return {
        "technology_id": tech_id,
        "status": "VERIFIED",
        "tool": tool,
        "reference_pin": reference_pin,
        "observed_tool_version": _tool_version(tool),
        "ci_tier": tier,
        "commands": commands,
    }


def build_many(
    registry: TowerRegistry,
    technology_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Build requested floors and represent every unknown request as an error row."""
    requested = list(technology_ids or [])
    selected = {value.casefold() for value in requested}
    known = {
        tech.get("id", "").casefold(): tech
        for tech in registry.technologies
        if isinstance(tech, dict) and isinstance(tech.get("id"), str)
    }
    rows = [
        build_floor(tech)
        for key, tech in known.items()
        if not selected or key in selected
    ]
    unknown = sorted({value for value in requested if value.casefold() not in known})
    rows.extend(_invalid(value, f"Unknown technology requested: {value}") for value in unknown)
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    return {
        "tower_id": registry.payload.get("tower_id", "UNKNOWN"),
        "requested_technology_ids": requested,
        "results": rows,
        "counts": dict(sorted(counts.items())),
    }


def write_report(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
