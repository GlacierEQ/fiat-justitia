# Branch Policy — `main` Is the Worker

`main` is the living integration branch, the only long-lived branch, and the source of truth for the Tower.

## Operating rules

1. **Completed work belongs on `main`.** A function is not complete while it exists only on a side branch.
2. **Branches are disposable workspaces.** Start from current `main`, keep the scope narrow, merge after exact-head verification, then delete the branch immediately.
3. **Normal branch count: zero or one active feature branch.** Two active branches is the hard operational ceiling and requires genuinely independent work.
4. **No stacked pull requests by default.** A temporary stack requires an explicit dependency record and must collapse into `main` as soon as its lower layer is ready.
5. **No stale preservation branches.** Git history, tags, releases, receipts, and artifacts preserve completed states; branches do not serve as archives.
6. **Exact-head evidence is mandatory.** Registry validation, generated-surface checks, tests, integrity verification, and relevant build gates must pass on the precise commit being merged.
7. **`main` must remain usable.** Broken or incomplete integration is repaired immediately or reverted; it is never hidden indefinitely behind another branch.

## Lifecycle

```text
current main
    → short-lived function branch
    → exact-head verification
    → merge into main
    → verify main tree
    → delete function branch
```

Exceptions must state the owner, dependency, exit condition, and deletion deadline in the pull request.
