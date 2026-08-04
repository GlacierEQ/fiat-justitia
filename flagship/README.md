# Tower Mission Pipeline

This is the flagship cross-language proof path.

| Stage | Technology | Responsibility |
|---|---|---|
| Contract | Protobuf | Define the shared mission, plan, decision, and event schema. |
| Bridge | ProtoJSON | Typed payload exchange between TypeScript and Python/Rust. |
| Ingress | TypeScript | Validate the operator mission and bind the input hash. |
| Planning | Python | Query the Tower-to-Megamind adapter. |
| Authority | Rust | Fail closed unless the plan is nonempty and registry-bound. |
| Telemetry | Go | Emit a typed execution event with evidence hash. |
| State | SQL | Persist constrained mission and event records. |
| Sandbox | WebAssembly | Demonstrate a capability-limited tool boundary. |
| Invariant | Lean 4 | Prove receipt sequence monotonicity. |
| Verification | Tower Receipt | Seal deterministic tamper-evident execution receipt. |

`flagship/run_pipeline.py` executes every available stage and records exact
toolchain blockers for unavailable floors.
