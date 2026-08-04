# Job Application Integration

The Tower of Babel participates in Casey Barton’s hardened recruiter package as the **technology placement and proof authority**.

## Authority boundary

The integration deliberately separates responsibilities:

- `GlacierEQ/job-application` owns the public recruiter front door.
- `GlacierEQ/job-app-helix` owns candidate identity, portfolio inventory, claim state, package composition, and evidence receipts.
- `GlacierEQ/the-tower-of-babel` owns technology responsibility, activation conditions, interoperability contracts, proof classes, build gates, and exact blockers.

Tower does not determine whether a candidate claim is recruiter-ready. Helix does not independently decide that a language or tool belongs at an architectural boundary. The package composes both authorities without merging them.

## Recruiter-facing interpretation

Tower is evidence of engineering judgment, not decorative polyglot signaling. Each admitted technology must answer:

1. What unique responsibility does it own?
2. Where does that responsibility live?
3. When does the technology activate?
4. Why should an existing component not own the boundary?
5. How is the claim compiled, tested, benchmarked, integrated, formally verified, or explicitly blocked?

At package pull commit `1028a58986be6bedd1d8d09a63593876aab52d1d`, Tower exposes 30 governed technology floors and 60 linked easy/advanced exhibits, including the Advanced Exhibit Atlas.

## Package projection

The hardened package projects Tower into:

- a human technology-engineering brief;
- an Advanced Exhibit Atlas snapshot;
- a candidate-facing machine contract;
- a repository synchronization receipt;
- a Mermaid portfolio graph connecting recruiter, evidence, and technology authorities.

The projection preserves Tower evidence states and blockers. It does not convert repository source into deployment proof or silently promote gated exhibits.

## Non-claims

This integration does not establish:

- production deployment of every Tower exhibit;
- portfolio-wide scale, performance, reliability, or customer impact;
- availability of hardware, toolchains, or external services marked as gated;
- superiority of a technology outside its declared responsibility.

## Release anchors

- Tower package pull: `1028a58986be6bedd1d8d09a63593876aab52d1d`
- Job-App Helix package pull: `1bcb70ab26b633a7b3cef7a3560a766b56917d80`
- Job-App Helix final-form release: `9942936b5fddf2bf5c4b64808253fdf9b0648d93`
- Job Application package pull: `1efb16a7017ebae0454d556c5ac31b4149c18673`

The recruiter ZIP and SHA-256 receipt are distributed as release artifacts and are not committed to Tower.
