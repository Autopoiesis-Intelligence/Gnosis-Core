# CI Regression Comparison — 2026-10-13

Scope: documentation-only PR #173 in `Autopoiesis-Intelligence/Gnosis-Core`. This record describes the exact runs below; it is not a general readiness or runtime claim.

## Exact comparison

- Base SHA: `78f84f6c6ac771478525b547ba467aa773e626b7`
- Base run: [38442736828](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/actions/runs/38442736828), job `115453185680`
- PR comparison run: [38446975018](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/actions/runs/38446975018), job `115467796858`
- Base log: 33 failed, 931 passed, 2 errors, 18 warnings.
- PR log: 33 failed, 931 passed, 2 errors, 18 warnings.
- Extracted failed/error test identifiers: 35 unique entries in each log; 35 common; zero base-only; zero PR-only.

Conclusion: these two runs support classifying the observed 35 failures/errors as already present on the cited base, rather than newly introduced by the documentation changes. This conclusion is limited to these exact runs and does not prove that a later PR HEAD passes CI.

## Later observed commit CI

For commit `1428cd5f422e0b8589285435c774d72d01555016`:

- Import Graph: PASS.
- CodeQL: PASS.
- Python 3.11 test job: FAIL; 33 failed, 931 passed, 2 errors.
- Python 3.12 test job: CANCELLED; its test step had failed before cancellation.
- Dependency Review: FAIL with explicit message: “Dependency review is not supported on this repository. Please ensure that Dependency graph is enabled.” This is a repository configuration blocker, not evidence by itself of vulnerable dependencies.

## Next action

1. Reconcile the exact current PR HEAD and inspect all checks for that SHA.
2. Keep source/test regressions separate from repository settings blockers.
3. Do not mark the PR CI-proven or merge it while required checks fail.
