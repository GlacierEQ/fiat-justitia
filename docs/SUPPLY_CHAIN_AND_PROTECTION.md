# Supply-Chain Provenance and Main Protection

The Tower separates repository-internal consistency from independently verifiable authorship and platform enforcement.

## Hash-locked Python CI

All Python-bearing workflows install `requirements/ci.lock` with `--require-hashes`, then install the Tower editable package with dependency resolution and build isolation disabled:

```bash
python -m pip install --require-hashes -r requirements/ci.lock
python -m pip install --no-deps --no-build-isolation -e .
```

The public package metadata retains compatibility ranges. CI uses exact reviewed versions and wheel digests.

## Immutable GitHub Actions

Permanent workflows reference full action commit SHAs. Dependabot proposes controlled GitHub Actions and Python updates through reviewable pull requests.

## Signed Tower evidence

On a push to `main`, Tower Verification attests these subjects:

- `artifacts/build-report.json`
- `artifacts/benchmarks.json`
- `artifacts/proof-report.json`
- `artifacts/tower_receipt.json`

`actions/attest-build-provenance` obtains a short-lived certificate through GitHub OIDC, emits SLSA build provenance in an in-toto statement, signs it through Sigstore, and associates the attestation with this repository.

Verify a downloaded subject with GitHub CLI:

```bash
gh attestation verify artifacts/tower_receipt.json --repo GlacierEQ/the-tower-of-babel
```

The deterministic Tower receipt remains useful for internal consistency. The external attestation proves which repository workflow produced the attested bytes.

## Main protection policy

`governance/main-ruleset.required.json` is the required platform policy. It protects `refs/heads/main` against deletion and non-fast-forward updates, requires pull requests and resolved review threads, requires branches to be current, and requires five stable exact-head contexts:

- `required-advanced-exhibit-gate`
- `required-nervous-system-contract`
- `required-quality-gate`
- `required-spiral-verification`
- `required-tower-verification`

Check live GitHub state:

```bash
python scripts/verify_main_ruleset.py
```

Install or update the ruleset using an administration-scoped token:

```bash
RULESET_ADMIN_TOKEN=... python scripts/apply_main_ruleset.py
python scripts/verify_main_ruleset.py
```

The `Main Ruleset Contract` workflow can perform the same operation after a repository secret named `RULESET_ADMIN_TOKEN` is configured with **Administration: write** permission. A scheduled strict verification reports future platform drift.

## Branch deletion authority

Branch Hygiene no longer scans merged branches or writes to `main`. It runs only after a same-repository PR merges. It deletes only that PR's head branch when:

1. the branch uses an approved temporary prefix;
2. it is not `main` or `HEAD`;
3. the remote branch still points to the exact SHA recorded in the merged PR event.

Every action produces a retained JSON deletion receipt. A moved branch fails closed and is not deleted.

## Semantic claim authority

`registry/advanced-claim-contracts.json` owns the Advanced Exhibit Atlas claims. Every floor declares source assertions, expected failure cases, required receipt fields, and forbidden positive overclaims. The audit verifies those contracts against checked-in source while allowing explicit disclaimers and claim-boundary language.
