# Spiral Engine — Civilization-Scale Admission

The Tower already declares that a capability becomes active only after the Spiral Engine returns an admission receipt. This module supplies the first executable form of that boundary.

## What it does

The engine performs two inspectable operations:

1. **Civilization question generation** — emits one `en-US` synthesis question spanning every governed civilization domain. A supplied seed makes the question replayable; omitting the seed creates a fresh seed and returns it with the question.
2. **Capability admission** — evaluates whole-system domain coverage, evidence, risk controls, observability, ownership, human override, and rollback readiness. The result is a deterministic `ADMIT` or `REJECT` receipt bound with SHA-256.

It performs no network calls and requires no model. A model may answer the generated question, but the activation decision remains ordinary, testable code.

## Domains

The initial civilization taxonomy is:

`science`, `technology`, `health`, `environment`, `economics`, `law`, `governance`, `history`, `culture`, `art`, `education`, `ethics`, `infrastructure`, `security`, `information`, `psychology`, `demographics`, and `geopolitics`.

Civilization-scoped capabilities must account for every domain. Unknown or missing domains produce exact blockers rather than being silently ignored.

## Commands

```bash
tower spiral question --seed civilization
tower spiral question --output artifacts/civilization-question.json

tower spiral admit examples/spiral/civilization_capability.json \
  --output artifacts/spiral-admission-receipt.json

tower spiral verify artifacts/spiral-admission-receipt.json
```

`tower spiral admit` exits `0` for `ADMIT`, `2` for a governed rejection, and `1` for invalid input or execution failure.

## Admission contract

A civilization-scale candidate provides:

- `capability_id`
- a substantive `summary`
- `scope: civilization`
- `risk_level`
- all governed `affected_domains`
- at least three independently identified evidence records with SHA-256 digests
- controls for ownership, approval, human override, audit logging, rollback, and metrics

The score is deliberately simple and reviewable:

| Dimension | Weight |
|---|---:|
| Domain coverage | 40% |
| Evidence | 30% |
| Controls | 30% |

Admission requires no blockers and a score of at least `0.85`.

## Receipt properties

Each receipt includes:

- the engine and schema versions
- the candidate SHA-256
- the exact decision, score, controls, evidence count, coverage, and blockers
- a stable receipt ID
- a receipt SHA-256 over canonical JSON

The receipt intentionally excludes wall-clock time so identical inputs produce identical receipts. External systems may timestamp, sign, notarize, or append the receipt without changing the Tower's deterministic decision.

## Activation status

This branch is a runtime candidate. The generated Tower registry remains `declared` until the implementation passes repository governance and is intentionally promoted through the canonical generation path.
