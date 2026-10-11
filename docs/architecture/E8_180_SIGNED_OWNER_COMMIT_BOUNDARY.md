# E8.180 — Signed owner authorization at the Core commit boundary

Status: **DESIGN / PARTIAL IMPLEMENTATION — NOT ACCEPTED**

This contract records the minimum safe integration boundary. A successful signature-verifier call alone is not execution authority.

## Current evidence

- PR #167 adds `gnosis/reflection/owner_authorization.py`, the PyNaCl dependency, and verifier contract tests.
- CI run #3555 for the branch after documentation commit `fcd142588dcc7fa883d8a7c2de79532908e84afe`: Python 3.11 reported **941 passed, 33 failed, 2 errors, 18 warnings**; Python 3.12 was cancelled after the Python 3.11 failure. This is **FAIL**, not acceptance. [Run #3555](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/actions/runs/38175590263).
- Import Graph #1736 and CodeQL #2436 passed. Dependency Review #977 failed; current evidence indicates the repository's GitHub Dependency Graph is disabled.
- The 33 failing tests include authority-boundary identity/legacy-validity failures, endogenous proposal binding, persistence/audit replay, reflection-gate API mismatch, and self-learning adapter tests; 2 errors are in real-commit failure-injection tests. This is a categorized log summary, not proof these failures are pre-existing. Exact base-SHA comparison remains outstanding.
- The current adapter still calls the legacy `require_trusted_execution(request, conn=..., actor=...)`; that gate does not verify a `ProductionAuthorization` signature.
- `execute_approved_core_proposal()` still constructs `SQLiteExecutionCommitAdapter()` without a trusted owner-authorization context.
- `issue_execution_authorization()` still raises `NotImplementedError`.
- The existing one-time authorization-consumption event is written inside the caller's SQLite transaction. It is not yet bound to successful production signature verification.
- No runtime or persisted end-to-end proof is established.

## Latest inspected CI failure detail

The Python 3.11 log ends with `941 passed, 33 failed, 2 errors, 18 warnings in 5.12s`. Representative failures include `test_execution_commit_gate_requires_all_boundaries` (`execution provenance identity is not canonical`), `test_sqlite_execution_commit_adapter_rejects_cross_candidate_substitution` (rejected earlier at missing authorization identity), and persistence/reflection API-contract failures. Do not change unrelated subsystems merely to make this PR green; first compare the exact failure set against the exact base SHA, then isolate regressions introduced by this branch.

## Required integration contract

1. A trusted application composition root owns the issuer-key resolver, active policy/scope, and trusted-time source. Request callers cannot supply or replace these dependencies.
2. Immediately before mutation, the commit boundary derives expected evolution identity, parent-state digest, request provenance, scope, and policy from the actual commit request and live parent state—not from the signed object itself.
3. The boundary verifies the Ed25519 signature, canonical authorization ID, key status/validity, expiry, scope, policy, evolution identity, parent digest, and request provenance against that independently derived context.
4. A successful verifier result is evidence only. It must be translated into the existing Core authorization boundary by trusted code; caller-created `ExecutionAuthorization`, `AuthorizationValidity`, booleans, strings, and digests cannot independently grant authority.
5. Authorization ID and nonce replay prevention must be durable and atomic with the Core transition. If verification, consumption, persistence, or post-persist state validation fails, the transaction must roll back.
6. The production execution entrypoint must use the trusted composition. No default path may silently fall back to the legacy boolean-only owner approval.
7. Keep the public/research collaboration authorization separate from Core mutation authority.

## Required adversarial end-to-end tests

- Valid signature for the exact current request commits once.
- Invalid signature, unknown/revoked/expired key, expired authorization, wrong scope/policy/evolution/parent digest/request provenance are rejected before durable mutation.
- Forged caller-created legacy authorization/validity objects do not bypass signature verification.
- Replaying either authorization ID or nonce is rejected.
- A failure after consumption but before completed transition rolls back both consumption and state mutation.
- Parent state advancing between authorization and commit is rejected.
- Receipt is produced only after persisted state matches the authorized proposed state.

## Acceptance gate

Do not mark this work complete until:
- tests exercise the actual production entrypoint and SQLite adapter;
- exact-head CI passes on supported Python versions;
- the exact base SHA is tested or otherwise compared with an evidence-backed baseline;
- replay/rollback tests prove transaction behavior;
- runtime/persisted evidence is recorded separately from unit-test evidence.

Do not merge the draft PR as production authorization integration while any item above remains open.
