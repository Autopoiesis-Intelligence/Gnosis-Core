# Production Authorization Verifier Contract — SEQ 116

**Status:** DESIGN PROPOSAL / NOT IMPLEMENTED  
**Base observed:** `3169a271bf31522273833c8aaf7f13417bd9faba`  
**Scope:** contract only. No production runtime, schema, migration, workflow, or key material changes are authorized by this document.

## 1. Security objective

Execution must be rejected unless the request carries an independently verifiable authorization issued under an explicitly configured trust root. Caller-constructible dataclasses, booleans, matching strings, self-reported validity metadata, and audit receipts are not proof of authority.

`IdentityMatch != AuthorityProof`  
`SignatureValid != AuthorityValid`  
`AuditIntegrity != AuthorizationTruth`

## 2. Required authorization artifact

A versioned signed artifact must bind at minimum:

- domain separator and protocol version;
- authorization ID and unique nonce;
- issuer ID and issuer key version;
- explicit authority scope / action class / audience;
- request provenance and exact evolution identity;
- parent state ID and parent state digest;
- execution intent snapshot digest, including candidate binding and proposed-state content identity;
- policy version and evidence digest;
- issued-at / not-before / expiry bounds, with a defined trusted-time policy;
- revocation and consumption lookup identity;
- delegation reference and constraints, if delegation is supported.

Canonical serialization must be deterministic. All security-relevant fields must be signed. Unknown versions, malformed encodings, unsupported algorithms and ambiguous field representations fail closed.

## 3. Trust root and key lifecycle

- Verification keys are supplied by an independently configured trust-root/key registry, never by the authorization object itself.
- The verifier resolves the exact issuer key version named in the artifact; it must not silently substitute the latest key.
- Unknown, disabled, expired or revoked issuer keys fail closed.
- Key rotation and revocation are explicit governed events with provenance.
- Private signing keys must not be committed to the repository, written to ordinary audit events, or stored in unprotected application tables.
- A test-only HMAC issuer is not a production issuer and must remain isolated from the production path.

The specific production algorithm, key custody system, trusted-time source and revocation authority remain architectural decisions; this document does not select or provision them.

## 4. Gate ordering

The pre-commit gate must establish, in this order, before any consumption audit event is written:

1. Authorization artifact is present and structurally valid.
2. Issuer and key version resolve through trusted configuration.
3. Cryptographic signature verifies over the canonical domain-separated payload.
4. Scope, audience, policy version and action class match the requested operation.
5. Request provenance, evolution identity, parent-state binding and complete intent snapshot match the actual candidate/transition.
6. Trusted-time validity and issuer/key lifecycle checks pass.
7. Revocation, persisted registry state and replay/consumption checks pass.
8. The existing canonical Core invariants and commit bindings pass.
9. Authorization consumption and state mutation occur atomically under the existing transaction contract.

Any failed check raises a fail-closed error and leaves no consumption event or state mutation. The gate must not consume first and validate later.

## 5. Transaction and concurrency obligations

- Consumption and the authority-sensitive state commit share the same transaction.
- A concurrent duplicate use must result in at most one accepted commit.
- A rollback must leave neither a consumption event nor a partial accepted state transition.
- A committed consumption must not be resurrected by restart/recovery.
- Unknown external outcomes must not be treated as successful execution receipts.

## 6. Required adversarial tests

At minimum, test:

- caller-constructed authorization without issuer proof;
- altered signature and altered payload;
- unknown issuer, unknown key version, unsupported algorithm;
- scope, audience, action, policy or evidence mismatch;
- cross-evolution replay and parent-state mismatch;
- intent/candidate/proposed-state substitution;
- expired and not-yet-valid authorization;
- revoked authorization and revoked issuer key;
- duplicate/replayed authorization under concurrency;
- registry row/payload/lifecycle tampering;
- rollback at each transaction boundary;
- process restart after consumption;
- missing verifier configuration;
- ensuring no consumption audit record exists on every pre-consumption rejection path.

The existing red diagnostic tests in PR #240 must become green only after the production gate rejects forged authorization and proves no consumption record was written.

## 7. Acceptance evidence

The implementation cannot be called complete based on this design, unit tests alone, or a successful signature check alone. Evidence must progress through:

`DESIGN → IMPLEMENTED → REACHABLE → RUNTIME → PERSISTED → AUDITED → CI_PROVEN`

For CI_PROVEN, record the exact commit SHA, workflow run IDs, test counts, failures/errors, and relevant runtime/persistence evidence. A green unrelated workflow does not close this gate.

## 8. Explicit non-goals

This proposal does not authorize:

- modifying production authorization/runtime code;
- changing database schema or migrations;
- inventing a production owner identity or silently treating a string as one;
- introducing a hidden global selector, clock or external operator into Ψ-Core;
- promoting the test issuer to production;
- merging the diagnostic PR or this design proposal.

## 9. Current observed blockers

At the inspected baseline, `TrustedOwnerIssuer.issue()` creates `ExecutionAuthorization(owner_approved=True)` after field comparisons without cryptographic verification. `require_trusted_execution()` validates caller-supplied `AuthorizationValidity` against values from the same object and consumes authorization after those checks. The existing test issuer is explicitly test/development-only and is not a production verifier integrated into this gate.

These observations describe the inspected base SHA above; re-check the current repository head before implementation.
