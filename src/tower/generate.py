'''Generate all derived Tower surfaces from the canonical registry.'''
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .registry import REPO_ROOT, TowerRegistry, load_registry, validate_registry

GENERATED_DIR = REPO_ROOT / "generated"


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, separators=(",", ":"), sort_keys=True) + "\n").encode("utf-8")


def _markdown_table(registry: TowerRegistry) -> str:
    rows = [
        "| # | Technology | Class | What | Where | When | Why | Evidence | Easy | Advanced |",
        "|---:|---|---|---|---|---|---|---|---|---|",
    ]
    for index, tech in enumerate(registry.technologies, 1):
        def esc(value: object) -> str:
            return str(value).replace("|", r"\|").replace("\n", " ")
        rows.append(
            f"| {index} | **{esc(tech['name'])}** `{esc(tech['extension'])}` | "
            f"{esc(tech['artifact_type'])} | {esc(tech['what'])} | {esc(tech['where'])} | "
            f"{esc(tech['when'])} | {esc(tech['why'])} | `{esc(tech['evidence_state'])}` / "
            f"`{esc(tech['proof_class'])}` | [{Path(tech['easy_example']).name}]({tech['easy_example']}) | "
            f"[{Path(tech['advanced_example']).name}]({tech['advanced_example']}) |"
        )
    return "\n".join(rows)


def render_readme(registry: TowerRegistry) -> str:
    count = len(registry.technologies)
    exhibit_count = count * 2
    behavioral_count = sum(
        1 for tech in registry.technologies if tech["proof_class"] == "behavioral"
    )
    formal_count = sum(
        1 for tech in registry.technologies if tech["proof_class"] == "formal"
    )
    gated_count = sum(
        1
        for tech in registry.technologies
        if tech["evidence_state"]
        in {"hardware_gated", "toolchain_gated", "service_gated"}
    )
    categories: dict[str, list[str]] = {}
    for tech in registry.technologies:
        categories.setdefault(tech["category"], []).append(tech["name"])
    coverage = "\n".join(
        f"- **{category.replace('_', ' ').title()}** — {', '.join(names)}"
        for category, names in sorted(categories.items())
    )
    return f"""# The Tower of Babel

> **An executable technology-selection, interoperability, and proof system for multi-language engineering.**

[![Tower Verification](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/tower.yml/badge.svg)](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/tower.yml)
[![Quality Gate](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/ci.yml/badge.svg)](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/ci.yml)
[![Spiral Engine](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/spiral.yml/badge.svg)](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/spiral.yml)

The Tower of Babel **decides where a technology belongs, explains why it belongs there, shows how it works, verifies the claim at the strongest available proof level, and exports the result for humans, software, and AI agents**.

It is not a language collection built for display. It is a governed engineering map: **{count} technology floors**, **{exhibit_count} linked exhibits**, versioned interface contracts, explicit blockers, executable build gates, and deterministic receipts. A floor earns its role through runtime behavior, safety, performance, hardware fit, or interoperability—not decorative polyglot signaling.

## The system in one minute

| Capability | What the Tower does |
|---|---|
| **Technology placement** | Records the What, Where, When, Why, and How for every admitted language, format, compiler layer, HDL, and proof system. |
| **Executable learning path** | Pairs each floor with an approachable exhibit and a substantive advanced implementation. |
| **Truthful verification** | Compiles, tests, benchmarks, integrates, or formally verifies a claim; unavailable dependencies return exact blockers instead of false success. |
| **Cross-language composition** | Publishes versioned interfaces so components cooperate without duplicating responsibility. |
| **Agent-readable authority** | Generates contracts for Megamind, Spiral Engine, Smithery publication metadata, build orchestration, maturity, and integration planning. |
| **Deterministic evidence** | Seals governed files and emits reproducible proof and release receipts. |

| Governed surface | Count |
|---|---:|
| Technology floors | **{count}** |
| Easy + advanced exhibits | **{exhibit_count}** |
| Behavioral proof floors | **{behavioral_count}** |
| Formal proof floors | **{formal_count}** |
| Explicitly gated floors | **{gated_count}** |

## From mission to receipt

```text
human objective / agent mission / system requirement
                         │
                         ▼
              Spiral or Megamind request
                         │
                         ▼
          canonical Tower technology contract
       placement · interfaces · owners · proof gate
                         │
                         ▼
         build / test / benchmark / formal check
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
   verified capability            exact blocker
          │                    toolchain · hardware
          ▼                       or service gate
  cross-language execution
          │
          ▼
 deterministic evidence receipt
```

A recruiter can see what the system accomplishes. An engineer can inspect execution and failure semantics. An agent initializes from the same canonical contracts without inventing a competing architecture.

## Start the Tower

```bash
python -m pip install -e .[dev]

tower validate
tower generate --check
tower integrity verify

tower spec rust
tower build rust
tower benchmark rust
tower megamind-map

tower spiral question \\
  --seed tower-demo \\
  --prompt-hint "safe multi-agent legal automation"

python flagship/run_pipeline.py
```

Run a complete portable governance pass:

```bash
tower build --all --allow-blocked --output artifacts/build-report.json
tower benchmark python c cpp rust go typescript webassembly \\
  --output artifacts/benchmarks.json
tower proof-report \\
  --build-report artifacts/build-report.json \\
  --benchmark-report artifacts/benchmarks.json \\
  --allow-blocked \\
  --output artifacts/proof-report.json
tower receipt \\
  --build-report artifacts/build-report.json \\
  --output artifacts/tower_receipt.json
```

## Inside the engine

`registry/tower.yml` is the root authority. It indexes governed `registry/tower.d/*.json` technology fragments and `registry/advanced-claim-contracts.json`; the README, Atlas, and every machine-readable projection are derived from that combined authority.

```text
registry/tower.yml + tower.d fragments + advanced claim contracts
                  │
                  ▼
        validation and path containment
                  │
                  ▼
        deterministic surface generation
                  │
        ┌─────────┼─────────┬──────────┬───────────┐
        ▼         ▼         ▼          ▼           ▼
     README   build map  interfaces  maturity  agent maps
        │         │         │          │           │
        └─────────┴─────────┴──────────┴───────────┘
                  │
                  ▼
       build · benchmark · proof · receipt
```

### The engineering contract

A technology is admitted only when the registry establishes:

- its unique responsibility and architectural boundary;
- its activation conditions and the reason another floor should not own the work;
- an easy exhibit and an advanced exhibit;
- a pinned toolchain reference, build/test commands, and execution tier;
- hardware, service, and toolchain constraints;
- cross-language interfaces and owning Megamind agents/pistons;
- an evidence state and proof class matching checked-in verification;
- a registry-owned semantic claim contract with source assertions, failure cases, receipt fields, and prohibited overclaims.

Working components are extended rather than rewritten for novelty. A new language must provide measurable value at a clear boundary without duplicating a component that already works.

### Flagship polyglot mission

```text
TypeScript ingress
    → ProtoJSON mission contract
Python planner
    → capability plan
Rust authority governor
    → allow / block decision
Go telemetry emitter
    → execution event
SQL canonical state
    → persisted mission
WebAssembly sandbox
    → constrained tool boundary
Lean 4
    → receipt-chain invariant
Tower receipt
```

See [`flagship/README.md`](flagship/README.md) and run `python flagship/run_pipeline.py`.

### Proof before promotion

| Evidence state | Meaning |
|---|---|
| `illustrative` | Teaches syntax or the central concept; no stronger runtime claim is made. |
| `compiles` | A pinned compiler or schema tool accepts the exhibit. |
| `tested` | Automated behavioral checks pass. |
| `benchmark` | A reproducible performance measurement exists. |
| `hardware_gated` | The implementation is present but requires declared hardware. |
| `toolchain_gated` | The implementation is present but its compiler is absent from portable CI. |
| `service_gated` | A declared external service is required. |
| `formally_verified` | A proof kernel accepts the theorem. |
| `integrated` | The floor participates in the flagship multi-language system. |
| `production_reference` | Operational failure handling, observability, and deployment evidence exist. |

## Advanced Exhibit Atlas

The easy exhibit teaches the technology. The advanced exhibit must own a real engineering boundary, expose failure behavior, and terminate in proof or an exact blocker. [`ADVANCED_EXHIBITS.md`](ADVANCED_EXHIBITS.md) publishes the signature engineering move and claim boundary for all {count} floors; [`quality/advanced_exhibit_atlas.json`](quality/advanced_exhibit_atlas.json) provides the same map to agents and automation.

## The thirty-floor map

The matrix is generated from the canonical registry. Change the registry and exhibits—not this README—to change a floor.

<details>
<summary><strong>Open the complete placement, proof, and exhibit matrix</strong></summary>

{_markdown_table(registry)}

</details>

### Domain coverage

{coverage}

## Machine entrypoint

An AI system should treat the Tower as an authority service, not prose to imitate.

1. **Initialize** from `registry/tower.yml` or the generated Megamind map.
2. **Resolve** a mission into capabilities and interfaces.
3. **Select** floors whose activation conditions and proof class satisfy the mission.
4. **Reject** duplicated ownership, missing evidence, and undeclared interfaces.
5. **Execute** through generated build contracts or governed adapters.
6. **Preserve** blockers, hashes, proof state, and receipts downstream.
7. **Promote** capability only through an explicit admission or evidence update.

### Generated contract library

| Surface | Role | Status |
|---|---|---|
| [`registry/tower.yml`](registry/tower.yml) | Canonical index and governance root | **Authored authority** |
| [`registry/advanced-claim-contracts.json`](registry/advanced-claim-contracts.json) | Source assertions, failure obligations, receipt fields, and truthful claim boundaries | **Authored authority** |
| [`generated/build_commands.json`](generated/build_commands.json) | Toolchains, pins, build/test commands, and execution tiers | Generated |
| [`generated/interfaces.json`](generated/interfaces.json) | Cross-language interface graph | Generated |
| [`generated/maturity.json`](generated/maturity.json) | Evidence state, proof class, and exhibit locations | Generated |
| [`generated/megamind.technology-map.json`](generated/megamind.technology-map.json) | Agent/piston ownership and activation map | Active export |
| [`integrations/megamind/`](integrations/megamind/) | Typed Tower-to-Megamind adapter contracts | Executable surface |
| [`generated/spiral-engine.registry.json`](generated/spiral-engine.registry.json) | Spiral metadata and technology edges | Declared metadata |
| [`src/tower/spiral.py`](src/tower/spiral.py) | Question, admission, override, audit, and receipt runtime | Operational-alpha |
| [`generated/smithery.registry.json`](generated/smithery.registry.json) | Smithery capability and publication contract | **Declared, not published** |
| [`generated/link_library.md`](generated/link_library.md) | Curated primary evidence for every floor | Generated library |
| [`.integrity/file_hashes.json`](.integrity/file_hashes.json) | SHA-256 ledger for governed artifacts | Sealed surface |
| [`docs/SUPPLY_CHAIN_AND_PROTECTION.md`](docs/SUPPLY_CHAIN_AND_PROTECTION.md) | Hash-locked CI, OIDC attestations, ruleset verification, and deletion receipts | Operational contract |

### Portfolio mesh

The Tower owns technology placement and proof. Connected repositories retain their own operational authority and consume Tower exports rather than maintaining competing registries.

| Repository | Relationship | Boundary |
|---|---|---|
| [`GlacierEQ/AKOS`](https://github.com/GlacierEQ/AKOS) | Governance and agent-orchestration authority | Canonical governance, evidence, completion, and operating-sequence contract. |
| [`GlacierEQ/aspen-grove-core`](https://github.com/GlacierEQ/aspen-grove-core) | Memory and context-continuity peer | Preserves durable context and continuity without competing with Tower placement authority. |
| [`GlacierEQ/apex-boot-core`](https://github.com/GlacierEQ/apex-boot-core) | Identity and initialization peer | Activates identity, capability, and initialization contracts before governed execution. |
| [`GlacierEQ/Pro_Code`](https://github.com/GlacierEQ/Pro_Code) | Engineering doctrine peer | Publishes standards, doctrine, and playbooks consumed by implementation systems. |
| [`GlacierEQ/pro-code`](https://github.com/GlacierEQ/pro-code) | Governed engineering-execution peer | Executes, verifies, cures, and persists engineering changes under shared governance. |
| [`GlacierEQ/job-app-helix`](https://github.com/GlacierEQ/job-app-helix) | Portfolio projection and evidence mesh | Presents capability and proof without becoming the technology authority. |
| [`GlacierEQ/apex-control-plane`](https://github.com/GlacierEQ/apex-control-plane) | Control-plane peer | Execution and automation surface that can consume governed selections. |
| [`GlacierEQ/apex-cli`](https://github.com/GlacierEQ/apex-cli) | Operator-facing peer | Command surface for downstream control-plane workflows. |
| [`flagship/`](flagship/) | In-repository integration proof | Executes the strict polyglot mission contract. |

External links describe curated portfolio relationships, not a claim that every repository is live-synchronized. Generated interfaces and ownership maps remain the machine-checkable integration source.

## Governance that survives automation

- `main` is the living worker; completed functionality lands there.
- Generated surfaces are never hand-edited; `tower generate --check` rejects drift.
- Every claim carries an evidence state, proof class, and registry-owned semantic claim contract.
- Blocked hardware, tools, and services remain visible and machine-readable.
- Cross-language interfaces are explicit and versioned.
- Megamind consumes Tower exports and does not maintain a competing registry.
- Smithery remains `declared-not-published` until an MCP package and external publication receipt exist.
- The Spiral runtime is executable; registry activation remains `declared` until governed promotion.
- Integrity, build evidence, proof reports, and receipts remain deterministic review surfaces; `main` receipts additionally receive OIDC-bound Sigstore provenance.

```text
edit canonical fragment
    → update easy + advanced exhibits
    → add or strengthen the proof gate
    → tower validate
    → tower generate
    → pytest
    → tower build --all --allow-blocked
    → reseal integrity
    → emit receipt
    → review exact-head CI
```

See [`AGENTS.md`](AGENTS.md) and [`BRANCH_POLICY.md`](BRANCH_POLICY.md).

## Truth boundary

The Tower is an **operational-alpha engineering authority**. It makes strong claims only where checked-in evidence supports them. Toolchain-, hardware-, and service-gated floors remain explicitly gated. Smithery publication is not claimed. External portfolio relationships are architectural contracts unless a repository contains and verifies a live adapter.

## License

MIT — see [`LICENSE`](LICENSE).
"""

def render_runtime_registry(registry: TowerRegistry) -> str:
    return '''#!/usr/bin/env python3
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
'''


def render_sidecar() -> str:
    return '''#!/usr/bin/env python3
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
'''


def build_surfaces(registry: TowerRegistry) -> dict[Path, bytes]:
    commands = {}
    interfaces: dict[str, list[str]] = {}
    maturity = {}
    megamind = {"tower_id": registry.payload["tower_id"], "technologies": {}}
    for tech in registry.technologies:
        tech_id = tech["id"]
        commands[tech_id] = {"toolchain": tech["toolchain"], "execution": tech["execution"]}
        interfaces[tech_id] = list(tech["interfaces"])
        maturity[tech_id] = {
            "evidence_state": tech["evidence_state"],
            "proof_class": tech["proof_class"],
            "easy_example": tech["easy_example"],
            "advanced_example": tech["advanced_example"],
        }
        megamind["technologies"][tech_id] = {
            "agents": tech["megamind"]["agents"],
            "pistons": tech["megamind"]["pistons"],
            "interfaces": tech["interfaces"],
            "activation_when": tech["when"],
            "proof_class": tech["proof_class"],
        }

    smithery = {
        "name": "tower-of-babel",
        "version": "1.1.0",
        "publication_status": "declared-not-published",
        "publication_rule": "Publication requires an MCP package plus an external registry receipt.",
        "capabilities": [f"technology:{row['id']}" for row in registry.technologies],
        "commands": ["validate", "build", "benchmark", "proof-report", "spec", "receipt", "megamind-map"],
        "source": "registry/tower.yml",
    }
    spiral = {
        "family": "tower-of-babel",
        "role": "canonical-technology-authority",
        "activation_status": "declared",
        "activation_rule": "A capability becomes active only after Spiral Engine returns an admission receipt.",
        "nodes": [row["id"] for row in registry.technologies],
        "edges": [
            {"from": tech_id, "to": interface, "type": "exposes_interface"}
            for tech_id, values in interfaces.items()
            for interface in values
        ],
    }
    links = ["# Tower Link Library", ""]
    for tech in registry.technologies:
        links.append(f"## {tech['name']}")
        links.extend(f"- {uri}" for uri in tech["primary_evidence"])
        links.append("")

    from .visualize import build_topology_graph, render_dot_graph

    surfaces: dict[Path, bytes] = {
        REPO_ROOT / "README.md": render_readme(registry).encode(),
        REPO_ROOT / "src" / "babel_registry.py": render_runtime_registry(registry).encode(),
        REPO_ROOT / "mastermind_sidecar.py": render_sidecar().encode(),
        REPO_ROOT / "src" / "tower" / "data" / "tower.yml": registry.source.read_bytes(),
        GENERATED_DIR / "build_commands.json": _json_bytes(commands),
        GENERATED_DIR / "interfaces.json": _json_bytes(interfaces),
        GENERATED_DIR / "maturity.json": _json_bytes(maturity),
        GENERATED_DIR / "megamind.technology-map.json": _json_bytes(megamind),
        GENERATED_DIR / "smithery.registry.json": _json_bytes(smithery),
        GENERATED_DIR / "spiral-engine.registry.json": _json_bytes(spiral),
        GENERATED_DIR / "link_library.md": ("\n".join(links) + "\n").encode(),
        GENERATED_DIR / "tower_topology.json": _json_bytes(build_topology_graph(registry)),
        GENERATED_DIR / "tower_interface_graph.dot": render_dot_graph(registry).encode(),
    }
    for fragment in registry.fragment_files:
        relative = fragment.relative_to(registry.source.parent)
        surfaces[REPO_ROOT / "src" / "tower" / "data" / relative] = fragment.read_bytes()
    return surfaces


def generate(*, check: bool = False) -> list[str]:
    registry = load_registry()
    errors = validate_registry(registry)
    if errors:
        return errors
    drift: list[str] = []
    for path, content in build_surfaces(registry).items():
        if check:
            if not path.is_file() or path.read_bytes() != content:
                drift.append(str(path.relative_to(REPO_ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    return drift


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors = generate(check=args.check)
    if errors:
        print("\n".join(errors))
        return 1
    print("Tower generated surfaces are current." if args.check else "Tower generated surfaces written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
