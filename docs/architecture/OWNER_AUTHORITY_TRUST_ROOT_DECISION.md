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
- evidence digest plus evidence type/version;
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
  -> verify validity/revocation
  -> enter existing transaction
  -> consume authorization once
  -> persist transition
  -> verify persisted result and audit evidence
```

Any rejection before consumption must leave domain state and consumption audit unchanged. Consumption and transition persistence must commit or roll back atomically. Unknown commit outcomes require explicit reconciliation; they must not be blindly retried.

## 5. Mandatory adversarial acceptance tests

1. Caller-constructed `ExecutionAuthorization(owner_approved=True)` without verified issuer proof is rejected.
2. Caller-constructed `AuthorizationValidity` cannot create authority.
3. Invalid signature, unknown key, revoked key, unsupported algorithm, wrong scope/policy, wrong provenance/evolution/parent, or evidence mismatch rejects before consumption.
4. Replaying a consumed authorization rejects.
5. Injected failures at each persistence boundary roll back consumption and state together.
6. Close/reopen recovery cannot resurrect rejected, consumed, expired, or revoked authority.
7. Positive execution succeeds only with a valid signature and exact matching intent.
8. End-to-end tests inspect durable state and audit after reopening SQLite.

## 6. Explicit non-goals and gates

This document does not implement a trusted issuer, establish a real-world owner identity, add an implicit clock, change database schema, or authorize mutation of Core invariants.

Implementation may begin only after the owner explicitly approves:
- the trust-root provisioning and key lifecycle;
- signature and canonical payload protocol;
- scope, validity, revocation and replay semantics;
- the exact runtime integration boundary.

After implementation, the acceptance bar remains exact commit SHA + passing required CI + adversarial runtime/persistence evidence. A green synthetic test alone is not sufficient.

**Current state: DESIGN ONLY. The safe default remains no execution authority until an independently verifiable issuer is available.**
