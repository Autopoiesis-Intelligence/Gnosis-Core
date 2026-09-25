# Federation CI Runtime Audit — 2026-09-25

## Observed run

CI run `2772` on commit `1a0e7afe2b612680aba0a4b7c159394e4657c3cd` reached test execution on Python 3.11/3.12. Package installation and test collection completed; the suite executed 896 tests in the 3.11 job.

Observed result: **874 passed, 27 failed**. Python 3.12 was cancelled after the 3.11 failure.

## Interpretation

The Federation boundary tests introduced in this branch were not present in the failure summary, so there is no observed evidence of a Federation-boundary failure in this run. However, the repository as a whole is **not green** and therefore the Federation/Core integration cannot be declared runtime-verified.

The failures are concentrated in existing persistence/recovery/reflection paths, including missing `authorization` arguments to `recover_instance`, missing `recovery_evidence_digest` / `load_candidate` names, an audit-evidence expectation mismatch, and a reflection-gate recovery failure.

These failures must be treated as independent Core regression blockers unless a later causal audit proves they were introduced by the Federation work.

## Gate status

- Federation package discovery: **VERIFIED by test execution reaching the suite**
- Federation boundary tests: **NO FAILURE OBSERVED in this run**
- Full repository CI: **FAILED**
- Federation → Core runtime proof: **NOT VERIFIED**
- Core regression baseline: **BLOCKED**

Do not mark the overall integration contract as 100% until a green CI run or a formally bounded exception proves the remaining failures are unrelated and independently controlled.
