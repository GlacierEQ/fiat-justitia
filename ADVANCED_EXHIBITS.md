# Advanced Exhibit Atlas

> A generated map of the engineering boundary, source assertions, failure cases, proof surface, and truthful claim limit for every advanced Tower exhibit.

The Atlas is generated from `registry/tower.yml` and `registry/advanced-claim-contracts.json`. It exposes distinctive implementation choices without converting them into unsupported novelty or production claims.

| Technology | Signature engineering move | Evidence | Advanced exhibit |
|---|---|---|---|
| **C** | Lock-free SPSC telemetry handoff — bounded queue, atomics, FIFO and backpressure receipt | `behavioral` / `behavioral` | [`advanced_lockfree_spsc_ring.c`](languages/c/advanced_lockfree_spsc_ring.c) |
| **C++** | Entropy-aware KV cache policy — deterministic utility scoring, pinned retention and decision fingerprint | `behavioral` / `behavioral` | [`advanced_kv_entropy.cpp`](languages/cpp/advanced_kv_entropy.cpp) |
| **Rust** | Typed side-effect safety governor — fail-closed path, payload, depth and approval policy | `behavioral` / `behavioral` | [`advanced_safety_governor.rs`](languages/rust/advanced_safety_governor.rs) |
| **Zig** | Mission-scoped allocator discipline — arena lifetime, deduplication and hard sample ceiling | `behavioral` / `behavioral` | [`advanced_arena_allocator.zig`](languages/zig/advanced_arena_allocator.zig) |
| **Odin** | Data-oriented thermal integration — explicit physical bounds, ablation and mission diagnostics | `integration` / `compile` | [`advanced_reentry_thermal.odin`](languages/odin/advanced_reentry_thermal.odin) |
| **Lua** | Mature lua proof surfaces — lua integration testing | `behavioral` / `behavioral` | [`advanced_sandbox_capability_table.lua`](languages/lua/advanced_sandbox_capability_table.lua) |
| **Python** | Drainable priority agent runtime — bounded queues, FIFO ties, futures, retries and graceful shutdown | `behavioral` / `behavioral` | [`advanced_async_orchestrator.py`](languages/python/advanced_async_orchestrator.py) |
| **Go** | Versioned telemetry trust boundary — CRC, frame bounds, sequence continuity, cancellation and metrics | `behavioral` / `behavioral` | [`advanced_telemetry_decoder.go`](languages/go/advanced_telemetry_decoder.go) |
| **TypeScript** | Governed MCP/JSON-RPC gateway — runtime validation, mutation approval, rate limiting and hashed receipts | `behavioral` / `behavioral` | [`advanced_mcp_gateway.ts`](languages/typescript/advanced_mcp_gateway.ts) |
| **Java** | Mature java proof surfaces — java integration testing | `behavioral` / `behavioral` | [`advanced_bounded_work_queue.java`](languages/java/advanced_bounded_work_queue.java) |
| **Kotlin** | Mature kotlin proof surfaces — kotlin integration testing | `behavioral` / `behavioral` | [`advanced_coroutine_supervisor.kt`](languages/kotlin/advanced_coroutine_supervisor.kt) |
| **Swift** | Metal affine-clamp engine — GPU dispatch with CPU reference and an explicit no-ANE claim boundary | `hardware` / `hardware` | [`advanced_metal_compute_engine.swift`](languages/swift/advanced_metal_compute_engine.swift) |
| **Elixir** | Supervised idempotent mission worker — duplicate rejection and observed process replacement after failure | `behavioral` / `behavioral` | [`advanced_fault_tolerant_beam.ex`](languages/elixir/advanced_fault_tolerant_beam.ex) |
| **Haskell** | Pure capability-policy AST validation — algebraic decisions, lexical path safety and deterministic receipt | `compile` / `compile` | [`advanced_ast_validator.hs`](languages/haskell/advanced_ast_validator.hs) |
| **R** | Exact Beta-Binomial decision analysis — ROPE, HDI and expected loss without MCMC or Bayes-factor overclaim | `behavioral` / `behavioral` | [`advanced_bayesian_ab_test.R`](languages/r/advanced_bayesian_ab_test.R) |
| **Julia** | Energy-audited orbital integration — velocity-Verlet propagation with conservation drift diagnostics | `behavioral` / `behavioral` | [`advanced_orbital_differential.jl`](languages/julia/advanced_orbital_differential.jl) |
| **Fortran** | Mature fortran proof surfaces — fortran integration testing | `behavioral` / `behavioral` | [`advanced_heat_diffusion.f90`](languages/fortran/advanced_heat_diffusion.f90) |
| **SQL / pgvector** | Tenant-isolated vector evidence store — HNSW retrieval, RLS, constraints and bounded search function | `integration` / `integration` | [`advanced_pgvector_hnsw.sql`](languages/sql/advanced_pgvector_hnsw.sql) |
| **CUDA C++ / PTX (NVIDIA Flagship)** | NVIDIA FlashAttention-v2 GPU kernel — NVIDIA FlashAttention-v2 shared-memory tiled GPU kernel | `illustrative` / `behavioral` | [`advanced_nvidia_flash_attention_kernel.cu`](languages/cuda/advanced_nvidia_flash_attention_kernel.cu) |
| **Triton** | Bounded fused single-query attention — one-program fusion, Torch oracle and latency benchmark | `hardware` / `benchmark` | [`advanced_fused_attention.py`](languages/triton/advanced_fused_attention.py) |
| **Mojo** | SIMD affine-clamp tensor kernel — explicit pointers and vector width without unsupported TPU branding | `integration` / `compile` | [`advanced_simd_tensor_kernel.mojo`](languages/mojo/advanced_simd_tensor_kernel.mojo) |
| **ONNX** | Portable top-k MoE router graph — model checking, reference execution and deterministic expert ordering | `behavioral` / `behavioral` | [`advanced_moe_router.py`](languages/onnx/advanced_moe_router.py) |
| **MLIR** | Destination-style attention score lowering — SSA tensor contract prepared for canonicalization and loop/vector passes | `integration` / `compile` | [`advanced_attention_pipeline.mlir`](languages/mlir/advanced_attention_pipeline.mlir) |
| **WebAssembly** | Capability- and fuel-bounded tool sandbox — memory bounds, denied-operation immutability and audit counters | `behavioral` / `behavioral` | [`advanced_wasm_sandbox.wat`](languages/wat/advanced_wasm_sandbox.wat) |
| **Protocol Buffers** | Cooling command and receipt contract — schema evolution, oneof authority, deterministic serialization and hashes | `behavioral` / `behavioral` | [`advanced_colossus_cooling.proto`](languages/protobuf/advanced_colossus_cooling.proto) |
| **FlatBuffers** | Hash-linked zero-copy telemetry frame — typed samples, file identity and prior-frame integrity field | `compile` / `compile` | [`advanced_telemetry.fbs`](languages/flatbuffers/advanced_telemetry.fbs) |
| **Cap'n Proto** | Capability-oriented agent mesh RPC — authority-bearing specialist references and typed receipts | `compile` / `compile` | [`advanced_agent_mesh.capnp`](languages/capnproto/advanced_agent_mesh.capnp) |
| **Verilog** | Weight-stationary dot-product datapath — registered coefficients, widened signed accumulation and valid timing | `compile` / `compile` | [`advanced_weight_stationary_dot_array.v`](languages/verilog/advanced_weight_stationary_dot_array.v) |
| **SystemVerilog** | Assertion-bearing 2x2 MAC mesh — explicit systolic dataflow and temporal accumulator invariants | `compile` / `compile` | [`advanced_systolic_array.sv`](languages/systemverilog/advanced_systolic_array.sv) |
| **VHDL** | Triple-modular-redundancy voter — majority result, mismatch signal and all-lanes-disagree assertion | `compile` / `compile` | [`advanced_fault_tolerant_voter.vhd`](languages/vhdl/advanced_fault_tolerant_voter.vhd) |
| **Chisel** | Parameterized NoC router generator — destination routing, round-robin arbitration and Decoupled backpressure | `integration` / `compile` | [`advanced_noc_router.scala`](languages/chisel/advanced_noc_router.scala) |
| **Lean 4** | Monotone authority and receipt proofs — kernel-checked action ordering and non-regressing sequence property | `formal` / `formal` | [`advanced_truth_gate_proof.lean`](languages/lean4/advanced_truth_gate_proof.lean) |
| **Coq** | Linked receipt-chain ordering proof — constructive chain-step and ordered-list invariants | `formal` / `formal` | [`advanced_receipt_chain.v`](languages/coq/advanced_receipt_chain.v) |
| **Agda** | Dependent capability lattice — total transitivity proof and impossible destructive downgrade case | `formal` / `formal` | [`advanced_capability_lattice.agda`](languages/agda/advanced_capability_lattice.agda) |
| **eBPF** | Kernel syscall sentinel — kernel syscall execve sentinel | `compile` / `compile` | [`advanced_syscall_sentinel.bpf.c`](languages/ebpf/advanced_syscall_sentinel.bpf.c) |
| **OpenQASM 3.0** | Grover search oracle circuit — 3-qubit Grover oracle superposition and diffusion | `integration` / `compile` | [`advanced_grover_oracle.qasm`](languages/openqasm/advanced_grover_oracle.qasm) |
| **Cairo** | STARK-provable state governor — STARK state governor receipt verification | `integration` / `compile` | [`advanced_stark_governor.cairo`](languages/cairo/advanced_stark_governor.cairo) |
| **JAX (xAI Grok Flagship)** | Grok-3 JAX distributed LLM mesh — Grok-3 distributed LLM mesh with RoPE attention, KV-caching, and sharding | `illustrative` / `behavioral` | [`advanced_grok_distributed_mesh.py`](languages/jax/advanced_grok_distributed_mesh.py) |
| **Soufflé Datalog** | Declarative static security scanner — declarative vulnerability taint flow | `compile` / `compile` | [`advanced_vulnerability_scanner.dl`](languages/datalog/advanced_vulnerability_scanner.dl) |
| **RHL-Quant (1.58b Ternary Quantization Flagship)** | Residual HLO-Lattice Quantization (RHL-Quant) — 1.58-bit Base Ternary Lattice with 2-bit Sparse Delta HLO Outlier Mesh | `illustrative` / `behavioral` | [`advanced_rhl_quant_engine.py`](languages/rhl_quant/advanced_rhl_quant_engine.py) |

## Machine-enforced claim contract

Every row is backed by registry-owned source patterns, expected failure cases, required receipt fields, and forbidden positive claims. The audit checks the source patterns and rejects unsupported positive claims while permitting explicit disclaimers and claim boundaries.

## Promotion standard

An exhibit is advanced only when it owns a meaningful boundary, rejects invalid or unsafe states, exposes an observable result, and carries a proof command or exact environmental blocker. File size, exotic syntax, and dramatic naming are not evidence.

## Originality boundary

The Tower highlights **distinctive synthesis**: original combinations of governance, receipts, bounded execution, cross-language interfaces, and proof surfaces. It does not claim that a standard algorithm, language feature, or architecture was invented here unless independently documented evidence supports that claim.
