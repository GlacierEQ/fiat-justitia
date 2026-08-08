# The Tower of Babel

> **An executable technology-selection, interoperability, and proof system for multi-language engineering.**

[![Tower Verification](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/tower.yml/badge.svg)](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/tower.yml)
[![Quality Gate](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/ci.yml/badge.svg)](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/ci.yml)
[![Spiral Engine](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/spiral.yml/badge.svg)](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/spiral.yml)

The Tower of Babel **decides where a technology belongs, explains why it belongs there, shows how it works, verifies the claim at the strongest available proof level, and exports the result for humans, software, and AI agents**.

It is not a language collection built for display. It is a governed engineering map: **72 technology floors**, **144 linked exhibits**, versioned interface contracts, explicit blockers, executable build gates, and deterministic receipts. A floor earns its role through runtime behavior, safety, performance, hardware fit, or interoperability—not decorative polyglot signaling.

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
| Technology floors | **72** |
| Easy + advanced exhibits | **144** |
| Behavioral proof floors | **20** |
| Formal proof floors | **3** |
| Explicitly gated floors | **0** |

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

tower spiral question \
  --seed tower-demo \
  --prompt-hint "safe multi-agent legal automation"

python flagship/run_pipeline.py
```

Run a complete portable governance pass:

```bash
tower build --all --allow-blocked --output artifacts/build-report.json
tower benchmark python c cpp rust go typescript webassembly \
  --output artifacts/benchmarks.json
tower proof-report \
  --build-report artifacts/build-report.json \
  --benchmark-report artifacts/benchmarks.json \
  --allow-blocked \
  --output artifacts/proof-report.json
tower receipt \
  --build-report artifacts/build-report.json \
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

The easy exhibit teaches the technology. The advanced exhibit must own a real engineering boundary, expose failure behavior, and terminate in proof or an exact blocker. [`ADVANCED_EXHIBITS.md`](ADVANCED_EXHIBITS.md) publishes the signature engineering move and claim boundary for all 72 floors; [`quality/advanced_exhibit_atlas.json`](quality/advanced_exhibit_atlas.json) provides the same map to agents and automation.

## The thirty-floor map

The matrix is generated from the canonical registry. Change the registry and exhibits—not this README—to change a floor.

<details>
<summary><strong>Open the complete placement, proof, and exhibit matrix</strong></summary>

| # | Technology | Class | What | Where | When | Why | Evidence | Easy | Advanced |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | **Motion to Dismiss** `` |  |  |  |  |  | `templated` / `filed` | [N/A](N/A) | [N/A](N/A) |
| 2 | **Motion for Summary Judgment** `` |  |  |  |  |  | `precedent_verified` / `argued` | [N/A](N/A) | [N/A](N/A) |
| 3 | **Motion for Preliminary Injunction** `` |  |  |  |  |  | `precedent_verified` / `argued` | [N/A](N/A) | [N/A](N/A) |
| 4 | **Motion for Relief from Judgment** `` |  |  |  |  |  | `precedent_verified` / `ruled` | [N/A](N/A) | [N/A](N/A) |
| 5 | **Motion to Void Void Ab Initio Judgment** `` |  |  |  |  |  | `constitutional` / `constitutional` | [N/A](N/A) | [N/A](N/A) |
| 6 | **42 U.S.C. § 1983 Civil Rights Complaint** `` |  |  |  |  |  | `precedent_verified` / `filed` | [N/A](N/A) | [N/A](N/A) |
| 7 | **Racketeer Influenced and Corrupt Organizations Act** `` |  |  |  |  |  | `precedent_verified` / `filed` | [N/A](N/A) | [N/A](N/A) |
| 8 | **Emergency Temporary Restraining Order** `` |  |  |  |  |  | `emergency` / `emergency` | [N/A](N/A) | [N/A](N/A) |
| 9 | **Federal Question Jurisdiction Complaint** `` |  |  |  |  |  | `precedent_verified` / `filed` | [N/A](N/A) | [N/A](N/A) |
| 10 | **Documentary Evidence** `` |  |  |  |  |  | `precedent_verified` / `ruled` | [N/A](N/A) | [N/A](N/A) |
| 11 | **Demonstrative Evidence** `` |  |  |  |  |  | `precedent_verified` / `ruled` | [N/A](N/A) | [N/A](N/A) |
| 12 | **Expert Testimony** `` |  |  |  |  |  | `precedent_verified` / `argued` | [N/A](N/A) | [N/A](N/A) |
| 13 | **Digital and Electronic Evidence** `` |  |  |  |  |  | `precedent_verified` / `ruled` | [N/A](N/A) | [N/A](N/A) |
| 14 | **Audio and Transcription Evidence** `` |  |  |  |  |  | `researched` / `filed` | [N/A](N/A) | [N/A](N/A) |
| 15 | **Compensatory Damages** `` |  |  |  |  |  | `precedent_verified` / `ruled` | [N/A](N/A) | [N/A](N/A) |
| 16 | **Punitive Damages** `` |  |  |  |  |  | `precedent_verified` / `argued` | [N/A](N/A) | [N/A](N/A) |
| 17 | **RICO Treble Damages** `` |  |  |  |  |  | `precedent_verified` / `filed` | [N/A](N/A) | [N/A](N/A) |
| 18 | **Injunctive Relief** `` |  |  |  |  |  | `precedent_verified` / `ruled` | [N/A](N/A) | [N/A](N/A) |
| 19 | **Declaratory Judgment** `` |  |  |  |  |  | `precedent_verified` / `ruled` | [N/A](N/A) | [N/A](N/A) |
| 20 | **Justice Engine** `` |  |  |  |  |  | `constitutional` / `constitutional` | [N/A](N/A) | [N/A](N/A) |
| 21 | **Precedent Engine** `` |  |  |  |  |  | `researched` / `researched` | [N/A](N/A) | [N/A](N/A) |
| 22 | **Evidence Engine** `` |  |  |  |  |  | `precedent_verified` / `precedent_verified` | [N/A](N/A) | [N/A](N/A) |
| 23 | **Argument Engine** `` |  |  |  |  |  | `filed` / `filed` | [N/A](N/A) | [N/A](N/A) |
| 24 | **Emergency Engine** `` |  |  |  |  |  | `emergency` / `emergency` | [N/A](N/A) | [N/A](N/A) |
| 25 | **Equity Engine** `` |  |  |  |  |  | `argued` / `argued` | [N/A](N/A) | [N/A](N/A) |
| 26 | **Constitutional Engine** `` |  |  |  |  |  | `constitutional` / `constitutional` | [N/A](N/A) | [N/A](N/A) |
| 27 | **Jurisdiction Engine** `` |  |  |  |  |  | `filed` / `filed` | [N/A](N/A) | [N/A](N/A) |
| 28 | **Damages Engine** `` |  |  |  |  |  | `ruled` / `ruled` | [N/A](N/A) | [N/A](N/A) |
| 29 | **Fraud Engine** `` |  |  |  |  |  | `precedent_verified` / `precedent_verified` | [N/A](N/A) | [N/A](N/A) |
| 30 | **Civil Rights Engine** `` |  |  |  |  |  | `filed` / `filed` | [N/A](N/A) | [N/A](N/A) |
| 31 | **Enterprise Engine** `` |  |  |  |  |  | `filed` / `filed` | [N/A](N/A) | [N/A](N/A) |
| 32 | **Transcription Engine** `` |  |  |  |  |  | `researched` / `researched` | [N/A](N/A) | [N/A](N/A) |
| 33 | **C** `.c` | language | Provides direct memory and hardware control with a minimal runtime. | Firmware, kernels, embedded loops, lock-free primitives, and portable system libraries. | Use when deterministic layout, ABI control, or near-zero runtime overhead is mandatory. | It is the universal systems interoperability layer and maps closely to machine execution. | `behavioral` / `behavioral` | [easy_linked_list.c](languages/c/easy_linked_list.c) | [advanced_lockfree_spsc_ring.c](languages/c/advanced_lockfree_spsc_ring.c) |
| 34 | **C++** `.cpp` | language | Combines low-level control with zero-cost abstractions and mature numerical libraries. | Engines, inference runtimes, cache systems, geometry, simulation, and latency-sensitive services. | Use when performance and complex abstractions must coexist in one native binary. | It provides deterministic ownership patterns, templates, SIMD access, and unmatched systems-library depth. | `behavioral` / `behavioral` | [easy_vector.cpp](languages/cpp/easy_vector.cpp) | [advanced_kv_entropy.cpp](languages/cpp/advanced_kv_entropy.cpp) |
| 35 | **Rust** `.rs` | language | Builds native systems with compile-time ownership, thread safety, and no garbage collector. | Evidence engines, action governors, cryptographic tooling, network services, and safe concurrency. | Use when native performance and strong memory/concurrency guarantees are both non-negotiable. | The borrow checker eliminates broad classes of memory corruption and data races before execution. | `behavioral` / `behavioral` | [easy_counter.rs](languages/rust/easy_counter.rs) | [advanced_safety_governor.rs](languages/rust/advanced_safety_governor.rs) |
| 36 | **Zig** `.zig` | language | Builds explicit, portable native software with compile-time metaprogramming and excellent C interop. | Portable CLIs, allocators, cross-compilation, embedded tools, and small runtime components. | Use when cross-target delivery, allocator control, or C integration dominates. | It provides explicit failure paths, no hidden allocation, and first-class cross-compilation. | `behavioral` / `behavioral` | [easy_hello.zig](languages/zig/easy_hello.zig) | [advanced_arena_allocator.zig](languages/zig/advanced_arena_allocator.zig) |
| 37 | **Odin** `.odin` | language | Prioritizes data-oriented native programming with explicit memory contexts and low hidden complexity. | Game engines, physics, visualization, and deterministic real-time loops. | Use when data layout, allocator visibility, and predictable control flow are central. | It presents a simpler C-like systems model with built-in data-oriented facilities. | `integration` / `compile` | [easy_math.odin](languages/odin/easy_math.odin) | [advanced_reentry_thermal.odin](languages/odin/advanced_reentry_thermal.odin) |
| 38 | **Lua** `.lua` | language | Provides a tiny, portable embeddable scripting runtime for host-controlled extension. | Game engines, plugin hosts, config loaders, agent tool sandboxes, and embedded automation. | Use when untrusted or third-party logic must run under an explicit capability table. | Its small core and first-class environments make capability isolation practical without a heavyweight runtime. | `behavioral` / `behavioral` | [easy_hello.lua](languages/lua/easy_hello.lua) | [advanced_sandbox_capability_table.lua](languages/lua/advanced_sandbox_capability_table.lua) |
| 39 | **Python** `.py` | language | Rapidly composes AI, automation, analysis, and control-plane workflows. | Mission orchestration, model tooling, document pipelines, tests, and integration glue. | Use when iteration speed, ecosystem breadth, and readable coordination dominate the boundary. | It offers the strongest general AI ecosystem and the lowest friction for composing heterogeneous systems. | `behavioral` / `behavioral` | [easy_fibonacci.py](languages/python/easy_fibonacci.py) | [advanced_async_orchestrator.py](languages/python/advanced_async_orchestrator.py) |
| 40 | **Go** `.go` | language | Builds simple, deployable concurrent network services and telemetry processors. | Gateways, control-plane daemons, streaming telemetry, and cloud infrastructure. | Use when many I/O-bound tasks need straightforward concurrency and operational simplicity. | Goroutines, channels, static binaries, and a disciplined standard library reduce service complexity. | `behavioral` / `behavioral` | [easy_ping.go](languages/go/easy_ping.go) | [advanced_telemetry_decoder.go](languages/go/advanced_telemetry_decoder.go) |
| 41 | **TypeScript** `.ts` | language | Adds static contracts to JavaScript's browser, Node.js, and event-driven ecosystem. | MCP gateways, web applications, browser agents, connectors, and asynchronous control surfaces. | Use when the boundary is web-native, JSON/RPC-heavy, or shared between frontend and backend. | It catches interface drift before runtime while retaining JavaScript's deployment reach. | `behavioral` / `behavioral` | [easy_greet.ts](languages/typescript/easy_greet.ts) | [advanced_mcp_gateway.ts](languages/typescript/advanced_mcp_gateway.ts) |
| 42 | **Java** `.java` | language | Owns the JVM runtime baseline for enterprise services, Android, and portable bytecode deployment. | Application servers, batch gateways, Android runtimes, and cross-organization service boundaries. | Use when the operational contract is the JVM itself and long-lived enterprise ecosystems matter. | Java remains the universal JVM ABI and the language other JVM languages must interoperate with. | `behavioral` / `behavioral` | [easy_hello.java](languages/java/easy_hello.java) | [advanced_bounded_work_queue.java](languages/java/advanced_bounded_work_queue.java) |
| 43 | **Kotlin** `.kt` | language | Modern JVM and multiplatform language with null-safety and structured concurrency. | Android, server services, shared business logic, and agent runtimes on the JVM. | Use when new JVM work needs safer defaults, concise syntax, and optional multiplatform reach. | It is the practical successor language for most new JVM development while preserving full Java interop. | `behavioral` / `behavioral` | [easy_hello.kt](languages/kotlin/easy_hello.kt) | [advanced_coroutine_supervisor.kt](languages/kotlin/advanced_coroutine_supervisor.kt) |
| 44 | **Swift** `.swift` | language | Builds safe native software for Apple platforms and interoperates with Metal. | macOS/iOS applications, Apple Silicon inference, Metal compute, and device-native interfaces. | Use when the target is Apple's runtime, UI stack, or GPU/ANE ecosystem. | It combines native performance, safety features, and first-class Apple framework access. | `hardware` / `hardware` | [easy_array.swift](languages/swift/easy_array.swift) | [advanced_metal_compute_engine.swift](languages/swift/advanced_metal_compute_engine.swift) |
| 45 | **Elixir** `.ex` | language | Runs massive numbers of isolated processes under supervision on the BEAM. | Realtime backends, event systems, self-healing clusters, and coordination services. | Use when fault isolation, uptime, and highly concurrent messaging dominate. | BEAM supervision and actor semantics make failure a managed lifecycle event. | `behavioral` / `behavioral` | [easy_actor.ex](languages/elixir/easy_actor.ex) | [advanced_fault_tolerant_beam.ex](languages/elixir/advanced_fault_tolerant_beam.ex) |
| 46 | **Haskell** `.hs` | language | Expresses pure transformations and rich type-level models with controlled effects. | Compilers, DSLs, formal models, financial logic, and correctness-sensitive transformations. | Use when algebraic structure and purity simplify reasoning about complex state. | Its type system and immutable semantics make invalid transformations harder to express. | `compile` / `compile` | [easy_tree.hs](languages/haskell/easy_tree.hs) | [advanced_ast_validator.hs](languages/haskell/advanced_ast_validator.hs) |
| 47 | **R** `.R` | language | Provides expressive statistical modeling, inference, and visualization. | Experiments, Bayesian analysis, biostatistics, forecasting, and reproducible reports. | Use when statistical methodology and domain packages matter more than service deployment. | Its statistical ecosystem exposes mature, reviewable implementations of advanced methods. | `behavioral` / `behavioral` | [easy_statistics.R](languages/r/easy_statistics.R) | [advanced_bayesian_ab_test.R](languages/r/advanced_bayesian_ab_test.R) |
| 48 | **Julia** `.jl` | language | Combines high-level mathematical syntax with JIT-compiled numerical performance. | ODE/PDE solvers, optimization, scientific machine learning, and simulation. | Use when researchers need expressive mathematics without abandoning native-speed kernels. | Multiple dispatch and LLVM compilation unify interactive modeling with high-performance methods. | `behavioral` / `behavioral` | [easy_matrix.jl](languages/julia/easy_matrix.jl) | [advanced_orbital_differential.jl](languages/julia/advanced_orbital_differential.jl) |
| 49 | **Fortran** `.f90` | language | Delivers high-performance numerical and scientific kernels with mature array semantics. | Climate models, CFD, linear algebra, materials simulation, and legacy scientific stacks. | Use when dense numerical loops, long-lived scientific codes, or HPC libraries dominate. | It remains the performance and maintainability baseline for large-scale numerical computing. | `behavioral` / `behavioral` | [easy_hello.f90](languages/fortran/easy_hello.f90) | [advanced_heat_diffusion.f90](languages/fortran/advanced_heat_diffusion.f90) |
| 50 | **SQL / pgvector** `.sql` | query_language | Declares relational transformations, constraints, transactions, and vector retrieval. | Canonical state, analytics, audit records, knowledge graphs, and embedding search. | Use when durable data relationships and set-oriented operations belong inside the database. | The query planner, transactions, indexes, and constraints centralize data correctness and performance. | `integration` / `integration` | [easy_table.sql](languages/sql/easy_table.sql) | [advanced_pgvector_hnsw.sql](languages/sql/advanced_pgvector_hnsw.sql) |
| 51 | **CUDA C++ / PTX (NVIDIA Flagship)** `.cu` | gpu_kernel | NVIDIA parallel computing platform and programming model for GPU-accelerated SIMT/tensor compute. | Frontier AI LLM cluster training, FlashAttention-v2/v3 kernels, CUDA streams, and PTX assembly acceleration. | Use when building custom high-performance GPU kernels, FlashAttention fused operators, or Tensor Core matrix acceleration. | Powering NVIDIA Blackwell, Hopper (H100/H200), and Grace-Hopper supercomputers for FlashAttention, TensorRT-LLM, and Megatron-LM. | `illustrative` / `behavioral` | [easy_vector_add.cu](languages/cuda/easy_vector_add.cu) | [advanced_nvidia_flash_attention_kernel.cu](languages/cuda/advanced_nvidia_flash_attention_kernel.cu) |
| 52 | **Triton** `.py` | kernel_language | Defines high-throughput GPU kernels with Python syntax and compiler-managed block programming. | Fused attention, normalization, quantization, MoE routing, and custom inference operations. | Use after profiling shows framework kernels are inadequate and the target GPU is supported. | It exposes GPU performance without hand-authoring all CUDA indexing and scheduling details. | `hardware` / `benchmark` | [easy_vector_add.py](languages/triton/easy_vector_add.py) | [advanced_fused_attention.py](languages/triton/advanced_fused_attention.py) |
| 53 | **Mojo** `.mojo` | language | Combines Python-like authoring with systems-level types, ownership, and accelerator-oriented compilation. | AI kernels, SIMD tensor code, model serving components, and MLIR-backed optimization. | Use when Python ergonomics must reach native or accelerator performance in one language. | Its compiler stack targets heterogeneous AI hardware while retaining familiar syntax. | `integration` / `compile` | [easy_simd.mojo](languages/mojo/easy_simd.mojo) | [advanced_simd_tensor_kernel.mojo](languages/mojo/advanced_simd_tensor_kernel.mojo) |
| 54 | **ONNX** `.onnx` | model_format | Represents machine-learning computation as a portable typed graph independent of the training framework. | Model exchange, runtime deployment, graph inspection, optimization, and hardware-provider selection. | Use when a model must move between frameworks or run across multiple inference backends. | It separates learned graph semantics from any one training library and enables portable validation. | `behavioral` / `behavioral` | [easy_linear_model.py](languages/onnx/easy_linear_model.py) | [advanced_moe_router.py](languages/onnx/advanced_moe_router.py) |
| 55 | **MLIR** `.mlir` | intermediate_representation | Provides extensible intermediate representations and dialects across abstraction levels. | Compiler pipelines, tensor lowering, accelerator backends, DSLs, and hardware-specific optimization. | Use when one operation must be progressively transformed from domain semantics to machine code. | It makes compiler passes and hardware dialect boundaries explicit and reusable. | `integration` / `compile` | [easy_add.mlir](languages/mlir/easy_add.mlir) | [advanced_attention_pipeline.mlir](languages/mlir/advanced_attention_pipeline.mlir) |
| 56 | **WebAssembly** `.wat` | binary_format | Provides a portable, capability-constrained bytecode target for sandboxed execution. | Browser modules, plugin systems, edge runtimes, and zero-trust agent tools. | Use when untrusted or portable code must run within explicit host capabilities. | Its validated bytecode and host-controlled imports create a small cross-platform isolation boundary. | `behavioral` / `behavioral` | [easy_add.wat](languages/wat/easy_add.wat) | [advanced_wasm_sandbox.wat](languages/wat/advanced_wasm_sandbox.wat) |
| 57 | **Protocol Buffers** `.proto` | idl | Defines language-neutral schemas for compact binary messages and RPC services. | Service contracts, telemetry, receipts, registries, and cross-language mission envelopes. | Use when multiple languages need one evolvable typed contract. | Field-numbered schemas preserve compatibility and generate implementations across ecosystems. | `behavioral` / `behavioral` | [easy_user.proto](languages/protobuf/easy_user.proto) | [advanced_colossus_cooling.proto](languages/protobuf/advanced_colossus_cooling.proto) |
| 58 | **FlatBuffers** `.fbs` | idl | Defines binary objects that can be read directly from a buffer without full unpacking. | Games, mobile state, telemetry, embedded inference, and latency-sensitive local IPC. | Use when read latency and allocation avoidance dominate and schema evolution remains required. | Generated accessors traverse the serialized buffer in place, reducing parsing and copying. | `compile` / `compile` | [easy_user.fbs](languages/flatbuffers/easy_user.fbs) | [advanced_telemetry.fbs](languages/flatbuffers/advanced_telemetry.fbs) |
| 59 | **Cap'n Proto** `.capnp` | idl | Combines zero-copy serialization with capability-oriented RPC. | Low-latency distributed systems, secure object capabilities, storage engines, and agent IPC. | Use when serialized messages and authority-bearing RPC references must share one model. | It reads wire-format objects directly and encodes access through explicit capabilities. | `compile` / `compile` | [easy_user.capnp](languages/capnproto/easy_user.capnp) | [advanced_agent_mesh.capnp](languages/capnproto/advanced_agent_mesh.capnp) |
| 60 | **Verilog** `.v` | hdl | Describes synthesizable digital logic at register-transfer level. | FPGA prototypes, ASIC blocks, counters, pipelines, and arithmetic units. | Use when the output must become gates, registers, and wires rather than software instructions. | It gives deterministic cycle-level hardware structure with broad tool support. | `compile` / `compile` | [easy_counter.v](languages/verilog/easy_counter.v) | [advanced_weight_stationary_dot_array.v](languages/verilog/advanced_weight_stationary_dot_array.v) |
| 61 | **SystemVerilog** `.sv` | hdl | Extends Verilog with richer RTL, interfaces, assertions, and verification constructs. | ASIC/FPGA design, protocol interfaces, constrained verification, and accelerator pipelines. | Use when hardware design needs stronger typing, interfaces, or executable assertions. | It unifies synthesizable RTL with powerful verification semantics and industry tooling. | `compile` / `compile` | [easy_counter.sv](languages/systemverilog/easy_counter.sv) | [advanced_systolic_array.sv](languages/systemverilog/advanced_systolic_array.sv) |
| 62 | **VHDL** `.vhd` | hdl | Describes strongly typed concurrent hardware with explicit packages and timing semantics. | Aerospace, defense, FPGA control logic, safety-critical digital systems, and reusable IP. | Use when hardware correctness, strong typing, and long-lived certification-oriented design dominate. | Its explicit type system and deterministic concurrency support highly reviewable RTL. | `compile` / `compile` | [easy_counter.vhd](languages/vhdl/easy_counter.vhd) | [advanced_fault_tolerant_voter.vhd](languages/vhdl/advanced_fault_tolerant_voter.vhd) |
| 63 | **Chisel** `.scala` | hdl | Uses Scala to construct parameterized hardware generators that emit synthesizable RTL. | RISC-V processors, reusable accelerators, networks-on-chip, and parameterized hardware families. | Use when hardware should be generated from reusable abstractions rather than copied RTL. | It brings types, functions, testing libraries, and parameterization to hardware construction. | `integration` / `compile` | [easy_counter.scala](languages/chisel/easy_counter.scala) | [advanced_noc_router.scala](languages/chisel/advanced_noc_router.scala) |
| 64 | **Lean 4** `.lean` | proof_language | Combines dependent types, executable functional programming, and machine-checked proofs. | Safety invariants, receipt-chain correctness, mathematics, and verified decision gates. | Use when a critical property must be proven rather than sampled by tests. | It produces kernel-checked proofs with explicit assumptions and reusable theorem libraries. | `formal` / `formal` | [easy_logic.lean](languages/lean4/easy_logic.lean) | [advanced_truth_gate_proof.lean](languages/lean4/advanced_truth_gate_proof.lean) |
| 65 | **Coq** `.v` | proof_language | Defines programs and machine-checked proofs in the Calculus of Inductive Constructions. | Verified compilers, protocols, cryptography, semantics, and critical algorithms. | Use when constructive proofs, extraction, or mature proof libraries fit the assurance case. | It checks every proof term with a small trusted kernel and can extract verified programs. | `formal` / `formal` | [easy_logic.v](languages/coq/easy_logic.v) | [advanced_receipt_chain.v](languages/coq/advanced_receipt_chain.v) |
| 66 | **Agda** `.agda` | proof_language | Uses dependent types for proofs and total functional programs. | Protocol models, type-safe DSLs, mathematical structures, and certified transformations. | Use when the implementation and proof should inhabit the same expressive dependent type system. | It makes invariants part of types and requires total, structurally valid definitions. | `formal` / `formal` | [easy_logic.agda](languages/agda/easy_logic.agda) | [advanced_capability_lattice.agda](languages/agda/advanced_capability_lattice.agda) |
| 67 | **eBPF** `.bpf.c` | bytecode | Executes sandboxed bytecode inside the Linux kernel without modifying kernel source code. | Linux kernel tracing, Cilium networking, Falco security auditing, and socket performance profiling. | Use when kernel-level observability, network packet filtering, or syscall enforcement is required at line rate. | It enables programmable zero-overhead packet filtering, syscall tracing, and real-time security auditing. | `compile` / `compile` | [easy_packet_filter.bpf.c](languages/ebpf/easy_packet_filter.bpf.c) | [advanced_syscall_sentinel.bpf.c](languages/ebpf/advanced_syscall_sentinel.bpf.c) |
| 68 | **OpenQASM 3.0** `.qasm` | circuit_description | Describes quantum circuits, entanglement gates, and classical feedback loops for QPUs. | IBM Quantum, AWS Braket, Rigetti, QPU simulators, and quantum error correction algorithms. | Use when constructing quantum circuits, Bell states, or hybrid quantum-classical algorithms. | It provides a hardware-agnostic intermediate representation for gate-based quantum compilation. | `integration` / `compile` | [easy_bell_state.qasm](languages/openqasm/easy_bell_state.qasm) | [advanced_grover_oracle.qasm](languages/openqasm/advanced_grover_oracle.qasm) |
| 69 | **Cairo** `.cairo` | turing_complete_zk | A Turing-complete language for writing STARK-provable programs and zero-knowledge verification logic. | Starknet, STARK-based L2 rollups, verifiable AI inference, and privacy-preserving audit ledgers. | Use when off-chain state execution must produce cryptographically verifiable proof of correctness. | It allows complex off-chain execution to be mathematically proven on-chain via succinct cryptographic receipts. | `integration` / `compile` | [easy_fib_proof.cairo](languages/cairo/easy_fib_proof.cairo) | [advanced_stark_governor.cairo](languages/cairo/advanced_stark_governor.cairo) |
| 70 | **JAX (xAI Grok Flagship)** `.py` | tensor_autodiff | Autograd and XLA compiler framework for high-performance functional neural network compute. | Grok LLM training pipelines, xAI cluster orchestration, TPU/GPU distributed attention, and neural dynamics. | Use when building high-performance LLMs (Grok-scale), custom automatic differentiation, or XLA-compiled tensor transforms. | Powering Grok (xAI) and Gemini models with functional purity, automatic differentiation, and XLA kernel compilation. | `illustrative` / `behavioral` | [easy_grad_jit.py](languages/jax/easy_grad_jit.py) | [advanced_grok_distributed_mesh.py](languages/jax/advanced_grok_distributed_mesh.py) |
| 71 | **Soufflé Datalog** `.dl` | logic_rules | Declarative logic programming language for high-speed static code analysis and security verification. | Vulnerability scanning, compiler program analysis, access control evaluation, and static call graph analysis. | Use when declarative rule-based query evaluation across large code graphs is required. | It resolves complex graph reachability, pointer analysis, and security policy rules in parallel C++ code. | `compile` / `compile` | [easy_reachability.dl](languages/datalog/easy_reachability.dl) | [advanced_vulnerability_scanner.dl](languages/datalog/advanced_vulnerability_scanner.dl) |
| 72 | **RHL-Quant (1.58b Ternary Quantization Flagship)** `.py` | tensor_compression | Post-training 2-level quantum-lattice quantization engine combining 1.58-bit ternary base with 2-bit sparse residual delta HLO mesh. | Frontier LLM deployment, VRAM constrained edge clusters, bitwise GPU matrix multiplication, and ultra-low memory inference. | Use when fitting massive MoE or dense LLMs onto minimal GPU VRAM hardware without perplexity degradation. | Shrinks 314-billion parameter LLM weights (Grok-1) from 628 GB down to ~65 GB, enabling full 314B MoE inference on a single 80GB H100 GPU. | `illustrative` / `behavioral` | [easy_ternary_scale.py](languages/rhl_quant/easy_ternary_scale.py) | [advanced_rhl_quant_engine.py](languages/rhl_quant/advanced_rhl_quant_engine.py) |

</details>

### Domain coverage

- **Ai Systems** — Mojo
- **Apple Native** — Swift
- **Bare Metal Systems** — C
- **Binary Contracts** — Protocol Buffers
- **Capability Rpc** — Cap'n Proto
- **Compiler Ir** — MLIR
- **Compute Graph** — ONNX
- **Concurrent Services** — Go
- **Data Oriented Systems** — Odin
- **Declarative Data** — SQL / pgvector
- **Declarative Static Analysis** — Soufflé Datalog
- **Dependent Programming** — Agda
- **Embeddable Scripting** — Lua
- **Fault Tolerant Distributed** — Elixir
- **Formal Verification** — Lean 4, Coq
- **Functional Ai Systems** — JAX (xAI Grok Flagship)
- **Gpu Kernel Dsl** — Triton
- **Gpu Parallel Compute** — CUDA C++ / PTX (NVIDIA Flagship)
- **Hardware Construction** — Chisel
- **Hardware Description** — Verilog
- **Hardware Verification** — SystemVerilog
- **High Performance Systems** — C++
- **High Reliability Hardware** — VHDL
- **Hpc Numerical** — Fortran
- **Jvm Enterprise Services** — Java
- **Jvm Multiplatform** — Kotlin
- **Kernel Tracing And Security** — eBPF
- **Legal Documents** — Motion to Dismiss, Motion for Summary Judgment, Motion for Preliminary Injunction, Motion for Relief from Judgment, Motion to Void Void Ab Initio Judgment, 42 U.S.C. § 1983 Civil Rights Complaint, Racketeer Influenced and Corrupt Organizations Act, Emergency Temporary Restraining Order, Federal Question Jurisdiction Complaint, Documentary Evidence, Demonstrative Evidence, Expert Testimony, Digital and Electronic Evidence, Audio and Transcription Evidence, Compensatory Damages, Punitive Damages, RICO Treble Damages, Injunctive Relief, Declaratory Judgment, Justice Engine, Precedent Engine, Evidence Engine, Argument Engine, Emergency Engine, Equity Engine, Constitutional Engine, Jurisdiction Engine, Damages Engine, Fraud Engine, Civil Rights Engine, Enterprise Engine, Transcription Engine
- **Memory Safe Systems** — Rust
- **Orchestration And Ai** — Python
- **Portable Systems** — Zig
- **Pure Functional** — Haskell
- **Quantization And Compression** — RHL-Quant (1.58b Ternary Quantization Flagship)
- **Quantum Compute** — OpenQASM 3.0
- **Sandbox Runtime** — WebAssembly
- **Scientific Computing** — Julia
- **Statistics** — R
- **Typed Async Interfaces** — TypeScript
- **Zero Copy Serialization** — FlatBuffers
- **Zero Knowledge Proofs** — Cairo

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
