# Owner Authority Trust-Root Decision

**Status:** PROPOSED DESIGN — NOT APPROVED; NO PRODUCTION IMPLEMENTATION AUTHORIZED  
**Baseline:** `main` at `b605781ef88fa88d30b3bc488cd17790cf02787b`  
**Scope:** Trust boundary only. No runtime, schema, migration, or Core-invariant changes are included.

## 1. Evidence motivating this decision

The current `ExecutionAuthorization` is a caller-constructible data object. Its `owner_approved` boolean and matching provenance/evolution strings do not prove who issued it. `AuthorizationValidity` is also caller-constructible and validates field consistency, not issuer authenticity.

On PR #229 HEAD `669ec89f938b2b41c3aab061327d27f31c9bc543`, CI run [38829092504](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/actions/runs/38829092504) reported 966 passed and 2 failed. The adapter-level adversarial test observed a caller-constructed authorization being accepted, the proposed state persisted, an authorization-consumption audit event recorded, and a result returned. This is evidence for that PR candidate and fixture, not a runtime proof against the exact current-main SHA.

The current main branch was independently inspected at `b605781ef88fa88d30b3bc488cd17790cf02787b`. It has the same fundamental trust-model gap: the authorization model has no issuer-verifiable signature or equivalent proof. Current-main CI status was not established in this audit.

## 2. Recommended trust-root model

**Recommendation for governance review:** use a pinned owner public key as the trust root, with Ed25519 signatures over a deterministic, domain-separated authorization payload.

The public key is configuration/trust material, not authority inferred from request fields. The private signing key must remain outside the Core repository and ordinary runtime logs. Core verifies the signature against an explicitly configured trusted key set; a caller cannot add or replace trusted keys through an execution request.

This recommendation is not yet an approved trust policy. Key provisioning, rotation, revocation, recovery, and operator responsibility require an explicit owner decision before implementation.

## 3. Required signed payload

The canonical signed payload must bind at minimum:

- protocol/domain identifier and payload version;
- issuer key identifier and key version;
- exact authority scope and policy version;
- request provenance and evolution identity;
- exact parent-state identity and digest;
- proposed-state digest/content ID and candidate binding digest;
- evidence digest plus evidence type/version;
- evaluation, shadow, invariant, and governance statuses;
- provenance ID and evaluator identity reference/version;
- unique authorization ID and nonce;
- validity/revocation reference and any delegation constraints.

Canonical encoding must be deterministic. Signatures must be domain-separated. Hashes, IDs, booleans, database rows, audit entries, and test fixtures are not substitutes for signature verification.

## 4. Required execution ordering

```text
untrusted request
  -> validate shape and canonical payload
  -> resolve explicitly trusted key
  -> verify signature and key status
  -> verify scope, policy, evidence, parent and exact evolution
  -> verify validity/revocation under the approved policy
  -> enter existing transaction
  -> consume authorization once
  -> persist transition
  -> verify persisted result and audit evidence
```

Any rejection before consumption must leave domain state and consumption audit unchanged. Consumption and transition persistence must commit or roll back atomically. Unknown commit outcomes require explicit reconciliation; they must not be blindly retried.

## 5. Mandatory adversarial acceptance tests

1. Caller-constructed `ExecutionAuthorization(owner_approved=True)` without verified issuer proof is rejected.
2. Caller-constructed `AuthorizationValidity` cannot create authority.
3. Invalid signature, unknown key, revoked key, unsupported algorithm/version, wrong scope/policy, wrong provenance/evolution/parent, or evidence mismatch rejects before consumption.
4. Replaying a consumed authorization rejects.
5. Injected failures at each persistence boundary roll back consumption and state together.
6. Close/reopen recovery cannot resurrect rejected, consumed, expired, or revoked authority.
7. Positive execution succeeds only with a valid signature and exact matching intent.
8. End-to-end tests inspect durable state and audit after reopening SQLite.
9. Forged-auth rejection and no-consumption are asserted independently, so an early assertion failure cannot hide a consumption side effect.
10. Canonical identity test vectors cover both empty and non-empty evaluator identity reference/version values.

## 6. Explicit non-goals and gates

This document does not implement a trusted issuer, establish a real-world owner identity, add an implicit clock, change database schema, or authorize mutation of Core invariants.

Implementation may begin only after the owner explicitly approves:
- the trust-root provisioning and key lifecycle;
- signature and canonical payload protocol;
- canonical evolution-identity field set and deterministic encoding;
- scope, validity, revocation and replay semantics;
- the exact runtime integration boundary and transaction ownership.

After implementation, the acceptance bar remains exact commit SHA + passing required CI + adversarial runtime/persistence evidence. A green synthetic test alone is not sufficient.

## 7. Canonical evolution-identity contract

There must be exactly one canonical identity definition reused by provenance creation, gate verification, signed authorization payload construction, receipts, and persistence cross-checks. Do not maintain a second manually copied field list in `authority.py`.

The canonical identity must bind candidate and execution IDs; parent state ID/digest; proposed state digest/content ID; candidate binding digest; evidence digest; evaluation, shadow, invariant, and governance statuses; provenance ID; and evaluator identity reference/version.

The exact-main source audit found that `EvidenceProvenance.evolution_identity` includes `evaluator_identity_ref` and `evaluator_identity_version`, while `_canonical_evolution_identity` in `authority.py` omits them. This is a separate identity-contract blocker. Do not resolve it by deleting evaluator fields or weakening equality checks. Define one shared canonical payload and use deterministic test vectors for empty and populated evaluator fields before treating end-to-end authorization as valid.

## 8. Exact-main diagnostic evidence — PR #231

PR #231 is a draft, test-only diagnostic based on the exact baseline SHA `b605781ef88fa88d30b3bc488cd17790cf02787b`. At tested head `5288b095058a5ec1d581274db9442afd420a9723`, CI run [38933265644](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/actions/runs/38933265644) reported 931 passed, 35 failed, and 2 errors.

On the controlled SQLite test path:
- `test_main_rejects_caller_constructed_authorization_before_consumption` failed because the expected `PermissionError` was not raised.
- An independent test found an `audit_events` row for `execution-authorization:forged-main-consumption-diagnostic`.

Compared with the prior observed run [38930210224](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/actions/runs/38930210224) (931 passed, 34 failed, 2 errors), the new diagnostic added one failure while the reported pass/error counts stayed unchanged. This comparison supports isolating the added diagnostic failure; it does not prove that every other failure is a baseline defect or that the runs are otherwise fully equivalent.

This is candidate CI evidence for a controlled test database. It does not establish a production state transition or prove every execution path. PR #231 must remain a diagnostic regression and must not be weakened merely to obtain a green suite.

**Current state: DESIGN ONLY. The safe default remains no execution authority until an independently verifiable issuer is available. PR #230 remains draft; no production implementation is authorized.**
