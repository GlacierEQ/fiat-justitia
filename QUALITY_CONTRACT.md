# Tower of Babel Quality Contract

The Tower is a governed systems portfolio, not a file-extension collection. Every exhibit must state truthfully what it proves, which toolchain evaluated it, and which limitations remain.

## Canonical authority

`registry/tower.yml` and its contained `registry/tower.d/*.json` fragments are the sole authored technology authority. Generated maturity, interface, build, Smithery, Spiral, and Megamind surfaces derive from that registry. This document defines quality expectations; it does not maintain a competing technology list or maturity ledger.

## Exhibit levels

### Easy

An easy exhibit teaches one technology-specific concept with minimal ceremony. It must:

- parse, compile, or execute with its documented toolchain when that toolchain is available;
- be deterministic and safe for the demonstrated input;
- contain enough context to run or inspect independently;
- avoid claiming production readiness.

### Advanced

An advanced exhibit demonstrates a credible engineering boundary. It must include:

1. **W4H+How rationale** — what, where, when, why, and how.
2. **Typed or explicit inputs and outputs.**
3. **Validation and failure behavior** for malformed, missing, or unsafe input.
4. **A meaningful invariant or policy boundary.**
5. **Observability** through metrics, receipts, diagnostics, or a structured report.
6. **A runnable demonstration, proof, benchmark, or test vector.**
7. **No placeholders** such as empty bodies, unconditional success, `pass`, or identity stubs.
8. **Bounded resource behavior** where concurrency, memory, network, hardware, or untrusted input is involved.

An advanced exhibit need not be a complete product. It must be honest evidence of the capability named in the canonical registry.

## Evidence and blockers

- `tested`, `compiles`, `benchmark`, `formally_verified`, and stronger states require corresponding execution evidence.
- Missing toolchains, services, dependencies, or hardware produce exact blockers, never false success.
- Structural presence is not compiler proof, and compiler proof is not production proof.
- `generated/maturity.json` is the generated maturity surface; `quality/exhibit_status.json` may add review notes but cannot override it.

## Repository invariants

CI fails when:

- the canonical registry is invalid or its fragments escape their governed boundary;
- generated surfaces drift from the registry;
- an easy or advanced exhibit is missing or malformed;
- native portable checks fail;
- a declared proof state conflicts with execution evidence;
- the immutable integrity ledger does not match the governed tree.

## Promotion rule

A capability becomes active only after its declared evidence gate succeeds and the Spiral Engine returns a valid admission receipt. Branch completion is not promotion: exact-head verification and integration into `main` are required.
