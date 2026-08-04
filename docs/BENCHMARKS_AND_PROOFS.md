# Benchmarks and Proof Results

The Tower does not publish universal language rankings. It publishes:

1. the exact command;
2. the pinned reference toolchain;
3. the machine and hardware boundary supplied by CI;
4. raw timing samples;
5. median, minimum, and maximum process time;
6. the evidence state and proof class;
7. exact blockers when execution is unavailable.

Run:

```bash
tower benchmark python c cpp rust go typescript webassembly
tower proof-report --build-report artifacts/build-report.json
```

Formal floors are considered proved only when their declared proof kernel accepts
the advanced exhibit. Hardware floors remain blocked unless the named device and
driver are explicitly enabled.
