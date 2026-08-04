# Fiat Justitia Ruat Caelum

> **"Let justice be done though the heavens fall."**

[![Justice Verification](https://github.com/GlacierEQ/fiat-justitia/actions/workflows/justice.yml/badge.svg)](https://github.com/GlacierEQ/fiat-justitia/actions/workflows/justice.yml)
[![Evidence Gate](https://github.com/GlacierEQ/fiat-justitia/actions/workflows/evidence.yml/badge.svg)](https://github.com/GlacierEQ/fiat-justitia/actions/workflows/evidence.yml)

An executable legal-engineering system for multi-jurisdictional litigation, evidence verification, and justice delivery.

## The system in one minute

| Capability | What Fiat Justitia does |
|---|---|
| **Document placement** | Records the What, Where, When, Why, and How for every admitted motion, complaint, evidence type, and remedy. |
| **Executable learning path** | Pairs each document type with an easy template and an advanced implementation. |
| **Truthful verification** | Researches, files, argues, and rules on a claim; unavailable precedents return exact blockers instead of false success. |
| **Cross-jurisdiction composition** | Publishes versioned interfaces so components cooperate without duplicating responsibility. |
| **Agent-readable authority** | Generates contracts for Megamind, Spiral Engine, build orchestration, maturity, and integration planning. |
| **Deterministic evidence** | Seals governed files and emits reproducible proof and justice receipts. |

| Governed surface | Count |
|---:|---:|
| Document types | **36** |
| Easy + advanced exhibits | **72** |
| Legal proof floors | **16** |
| Constitutional proof floors | **3** |
| Explicitly gated floors | **9** |

## From injustice to justice

```text
human rights violation / agent mission / system requirement
                         │
                         ▼
              Spiral or Megamind request
                         │
                         ▼
          canonical Fiat Justitia document contract
       placement · interfaces · owners · proof gate
                         │
                         ▼
         research · file · argue · rule
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
   verified justice               exact blocker
          │                    jurisdiction · precedent
          ▼                       or procedural gate
  cross-jurisdiction execution
          │
          ▼
 deterministic evidence receipt
```

A judge can see what the system accomplishes. An attorney can inspect execution and failure semantics. An agent initializes from the same canonical contracts without inventing a competing architecture.

## Start Fiat Justitia

```bash
python -m pip install -e .[dev]

fiat validate
fiat generate --check
fiat integrity verify

fiat spec motion-dismiss
fiat build motion-dismiss
fiat benchmark motion-dismiss
fiat megamind-map

fiat spiral question \
  --seed fiat-demo \
  --prompt-hint "safe multi-agent legal automation"

python flagship/run_pipeline.py
```

Run a complete portable governance pass:

```bash
fiat build --all --allow-blocked --output artifacts/build-report.json
fiat benchmark motion complaint evidence remedy precedent \
  --output artifacts/benchmarks.json
fiat proof-report \
  --build-report artifacts/build-report.json \
  --benchmark-report artifacts/benchmarks.json \
  --allow-blocked \
  --output artifacts/proof-report.json
fiat receipt \
  --build-report artifacts/build-report.json \
  --output artifacts/fiat_receipt.json
```

## Inside the engine

`registry/tower.yml` is the root authority. It indexes governed `registry/tower.d/*.json` legal fragments and `registry/advanced-claim-contracts.json`; the README, Atlas, and every machine-readable projection are derived from that combined authority.

## Legal Proof Classes

| Proof Class | Description |
|---|---|
| `draft` | Document drafted, not yet filed |
| `researched` | Legal research completed |
| `templated` | Template created and tested |
| `precedent_verified` | Case law verified |
| `filed` | Filed with court |
| `argued` | Oral argument delivered |
| `ruled` | Court ruled on motion |
| `appellate_reviewed` | Appellate court reviewed |
| `supreme_certified` | Supreme Court certiorari |
| `constitutional` | Constitutional question certified |

## Mission

This system exists to ensure that justice is done, regardless of the cost. It is not a legal collection built for display. It is a governed engineering map: **36 document floors**, **72 linked exhibits**, versioned interface contracts, explicit blockers, executable build gates, and deterministic receipts. A floor earns its role through legal merit, precedent, and constitutional authority—not decorative polyglot signaling.

**Fiat justitia ruat caelum.**
