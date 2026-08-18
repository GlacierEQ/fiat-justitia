# Tower Agent Doctrine

## Authority

The APEX registry rooted at `registry/tower.yml` is the active authority for:

- technology admission;
- W4H+How placement;
- easy and advanced exhibit paths;
- evidence state and proof class;
- toolchain and build commands;
- hardware and service blockers;
- cross-language interfaces;
- Megamind agent and piston ownership.

Do not add a language, format, compiler, HDL, proof system, or runtime by editing
the README, sidecar, generated files, or Megamind maps directly.

## Required workflow

1. Change the APEX index or one of its declared fragments.
2. Add or update both exhibits.
3. Add or update the proof gate.
4. Run `tower validate`.
5. Run `tower generate`.
6. Run `pytest`.
7. Run `tower build --all --allow-blocked`.
8. Generate and verify integrity.
9. Generate the deterministic receipt.
10. Review generated drift before commit.

## Truth classes

A file name containing `advanced` does not establish production maturity.
Use the declared evidence state:

- illustrative
- compiles
- tested
- benchmark
- hardware_gated
- toolchain_gated
- service_gated
- formally_verified
- integrated
- production_reference

Never promote a floor without corresponding evidence.

## Language-diversification rule

New technology is admitted only when its What, Where, When, Why, How,
interoperability boundary, owner, and proof gate are explicit. Existing working
components are preserved; no refactor is permitted merely to introduce another
language.

## Generated files

Generated surfaces must not be hand-edited. They are overwritten by
`python3 -m tower.generate`.
