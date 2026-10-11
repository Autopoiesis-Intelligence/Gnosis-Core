# E8.180 — Signed owner authorization at the Core commit boundary

Status: **DESIGN / PARTIAL IMPLEMENTATION — NOT ACCEPTED**

This contract records the minimum safe integration boundary. A successful signature-verifier call alone is not execution authority.

## Current evidence

- PR #167 adds `gnosis/reflection/owner_authorization.py`, the PyNaCl dependency, and verifier contract tests.
- CI for PR #167 head `207d7ec9846c85d1bff3f16431e3870068d7fe8b` reported Python 3.12: 941 passed, 33 failed, 2 errors. This is **FAIL**, not acceptance.
- Import Graph and CodeQL checks passed for the run inspected. Dependency Review failed because GitHub Dependency Graph is disabled.
- The current adapter still calls the legacy `require_trusted_execution(request, conn=..., actor=...)`; that gate does not verify a `ProductionAuthorization` signature.
- `execute_approved_core_proposal()` still constructs `SQLiteExecutionCommitAdapter()` without a trusted owner-authorization context.
- `issue_execution_authorization()` still raises `NotImplementedError`.
- The existing one-time authorization-consumption event is written inside the caller's SQLite transaction. It is not yet bound to successful production signature verification.
- No runtime or persisted end-to-end proof is established.

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
