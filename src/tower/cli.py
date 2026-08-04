"""Tower command-line interface."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .benchmark import benchmark_many, write_benchmark
from .build import build_many, write_report
from .generate import generate
from .integrity import verify_integrity, write_manifest
from .proofs import build_proof_report, write_proof_report
from .receipt import write_receipt
from .registry import load_registry, validate_registry
from .spiral import (
    build_admission_receipt,
    generate_civilization_question,
    read_json_object,
    verify_admission_receipt,
    write_json,
)


def _print(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def _read_json_object(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"{label} not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is unreadable or invalid JSON: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} root must be an object: {path}")
    return payload


def _status_count(counts: dict[str, Any], predicate) -> int:
    return sum(
        count for status, count in counts.items()
        if isinstance(status, str) and isinstance(count, int) and predicate(status)
    )


def main() -> int:
    parser = argparse.ArgumentParser(prog="tower")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    gen = sub.add_parser("generate")
    gen.add_argument("--check", action="store_true")
    spec = sub.add_parser("spec")
    spec.add_argument("technology")
    build = sub.add_parser("build")
    build.add_argument("technologies", nargs="*")
    build.add_argument("--all", action="store_true")
    build.add_argument("--allow-blocked", action="store_true")
    build.add_argument("--output", default="artifacts/build-report.json")
    integrity = sub.add_parser("integrity")
    integrity.add_argument("action", choices=["generate", "verify"])
    benchmark = sub.add_parser("benchmark")
    benchmark.add_argument("technologies", nargs="+")
    benchmark.add_argument("--iterations", type=int, default=3)
    benchmark.add_argument("--allow-blocked", action="store_true")
    benchmark.add_argument("--output", default="artifacts/benchmarks.json")
    proof = sub.add_parser("proof-report")
    proof.add_argument("--build-report", default="artifacts/build-report.json")
    proof.add_argument("--benchmark-report", default="artifacts/benchmarks.json")
    proof.add_argument("--allow-blocked", action="store_true")
    proof.add_argument("--output", default="artifacts/proof-report.json")
    receipt = sub.add_parser("receipt")
    receipt.add_argument("--build-report", default="artifacts/build-report.json")
    receipt.add_argument("--output", default="artifacts/tower_receipt.json")

    spiral = sub.add_parser("spiral")
    spiral_sub = spiral.add_subparsers(dest="spiral_action", required=True)
    spiral_question = spiral_sub.add_parser("question")
    spiral_question.add_argument("--seed")
    spiral_question.add_argument("--prompt-hint")
    spiral_question.add_argument("--output")
    spiral_admit = spiral_sub.add_parser("admit")
    spiral_admit.add_argument("candidate")
    spiral_admit.add_argument(
        "--output",
        default="artifacts/spiral-admission-receipt.json",
    )
    spiral_verify = spiral_sub.add_parser("verify")
    spiral_verify.add_argument("receipt")

    sub.add_parser("report")
    sub.add_parser("megamind-map")

    search_parser = sub.add_parser("search")
    search_parser.add_argument("query")

    visualize_parser = sub.add_parser("visualize")
    visualize_parser.add_argument("--format", choices=["json", "dot"], default="json")

    args = parser.parse_args()

    try:
        registry = load_registry()
        if args.command == "validate":
            errors = validate_registry(registry)
            _print({"valid": not errors, "technology_count": len(registry.technologies), "errors": errors})
            return 0 if not errors else 1
        if args.command == "generate":
            errors = generate(check=args.check)
            _print({"valid": not errors, "drift": errors})
            return 0 if not errors else 1
        if args.command == "spec":
            row = registry.by_id(args.technology)
            _print(row or {"error": "UNKNOWN_TECHNOLOGY", "technology": args.technology})
            return 0 if row else 1
        if args.command == "build":
            selected = None if args.all else args.technologies
            if not args.all and not selected:
                parser.error("build requires --all or at least one technology id")
            report = build_many(registry, selected)
            write_report(report, Path(args.output))
            _print(report)
            counts = report.get("counts", {})
            failed = _status_count(counts, lambda status: status in {"FAILED", "FAILED_TIMEOUT", "INVALID_MANIFEST"})
            blocked = _status_count(counts, lambda status: status.startswith("BLOCKED_"))
            if failed:
                return 1
            if blocked and not args.allow_blocked:
                return 2
            return 0
        if args.command == "benchmark":
            report = benchmark_many(registry, args.technologies, iterations=args.iterations)
            write_benchmark(report, Path(args.output))
            _print(report)
            statuses = {str(row.get("status", "")) for row in report.get("results", []) if isinstance(row, dict)}
            if statuses & {"FAILED", "FAILED_TIMEOUT", "INVALID_BENCHMARK", "INVALID_MANIFEST"}:
                return 1
            if any(status.startswith("BLOCKED_") for status in statuses) and not args.allow_blocked:
                return 2
            return 0
        if args.command == "proof-report":
            build_report = _read_json_object(Path(args.build_report), "build report")
            benchmark_path = Path(args.benchmark_report)
            benchmark_report = _read_json_object(benchmark_path, "benchmark report") if benchmark_path.is_file() else None
            report = build_proof_report(registry, build_report, benchmark_report)
            write_proof_report(report, Path(args.output))
            _print(report)
            counts = report.get("counts", {})
            if counts.get("FAILED", 0):
                return 1
            incomplete = counts.get("BLOCKED", 0) + counts.get("NOT_EXECUTED", 0)
            return 0 if args.allow_blocked or not incomplete else 2
        if args.command == "integrity":
            if args.action == "generate":
                _print(write_manifest())
                return 0
            result = verify_integrity()
            _print(result)
            return 0 if result["ok"] else 1
        if args.command == "receipt":
            build_report = _read_json_object(Path(args.build_report), "build report")
            payload = write_receipt(Path(args.output), build_report)
            _print(payload)
            valid = payload["registry_valid"] and payload["integrity_valid"] and payload["build_report_valid"]
            return 0 if valid else 1
        if args.command == "spiral":
            if args.spiral_action == "question":
                payload = generate_civilization_question(args.seed, prompt_hint=args.prompt_hint)
                if args.output:
                    write_json(Path(args.output), payload)
                _print(payload)
                return 0
            if args.spiral_action == "admit":
                candidate = read_json_object(Path(args.candidate))
                payload = build_admission_receipt(candidate)
                write_json(Path(args.output), payload)
                _print(payload)
                return 0 if payload["decision"] == "ADMIT" else 2
            if args.spiral_action == "verify":
                payload = read_json_object(Path(args.receipt))
                result = verify_admission_receipt(payload)
                _print(result)
                return 0 if result["ok"] else 1
        if args.command == "report":
            _print(_read_json_object(Path("generated/maturity.json"), "maturity report"))
            return 0
        if args.command == "megamind-map":
            _print(_read_json_object(Path("generated/megamind.technology-map.json"), "Megamind map"))
            return 0
        if args.command == "search":
            from .visualize import search_registry
            results = search_registry(registry, args.query)
            _print({"query": args.query, "count": len(results), "matches": results})
            return 0
        if args.command == "visualize":
            from .visualize import build_topology_graph, render_dot_graph
            if args.format == "dot":
                print(render_dot_graph(registry))
            else:
                _print(build_topology_graph(registry))
            return 0
    except ValueError as exc:
        _print({"error": type(exc).__name__, "message": str(exc)})
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
