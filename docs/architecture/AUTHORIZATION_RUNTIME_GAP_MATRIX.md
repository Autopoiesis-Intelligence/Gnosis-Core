# Authorization Runtime Gap Matrix

**Status:** Evidence-based audit; no production remediation is implemented by this document.
**Inspected base:** `3169a271bf31522273833c8aaf7f13417bd9faba`
**Related contract:** `docs/architecture/TRANSACTION_CONTRACT.md`, E5.05–E5.13
**Related PR:** #241 (Draft)

## Purpose

Avoid duplicating already-defined security theory. Map existing requirements to the current implementation and identify which concrete runtime components are still missing. A contract statement is not implementation evidence.

## Gap matrix

| Requirement | Existing contract | Observed source evidence | Status |
|---|---|---|---|
| Trusted issuer / independent root of trust | E5.05-A, E5.06 | `trusted_issuer.py` compares caller-provided strings/fields; `authority.py` retains explicit `NotImplementedError` issuer boundary | NOT IMPLEMENTED |
| Cryptographic authorization proof | E5.07 | No production signature verifier/key resolver established; `test_issuer.py` is explicitly non-production HMAC test code | NOT IMPLEMENTED |
| Canonical domain-separated signed payload | E5.07–E5.08 | Test issuer has its own canonical payload; no production verifier path is wired to the execution gate | TEST-ONLY / NOT INTEGRATED |
| Key version, rotation, disablement and revocation authority | E5.06–E5.07 | Contract specifies lifecycle semantics; no authoritative production key registry/provider established | CONTRACT ONLY |
| Trusted time and expiry | E5.05-B, E5.06 | Test-only lifecycle checks exist; production trusted-time source is not established | TEST-ONLY / BLOCKED |
| Exact provenance/evolution/parent/policy/intent binding | E5.05-B, E5.07–E5.08, E5.13 | Existing authorization/intent binding checks exist, but they do not prove issuer authenticity | PARTIAL; NOT AUTHORITY PROOF |
| Reject before consumption event | E5.05-B and transaction contract | Gate consumes within the adapter transaction, but current gate lacks an independent signature-verification step | INCOMPLETE SECURITY GATE |
| Atomic consume + state commit | Transaction contract / execution adapter | Adapter wraps trusted gate and transition persistence in a transaction | STRUCTURE PRESENT; END-TO-END SECURITY NOT PROVEN |
| Resolver/provider cannot be caller-substituted | `docs/EXECUTION_PLAN.md`, E7.76 | Execution plan says resolver API accepts injected callables and is not wired to a protected production provider | NOT IMPLEMENTED |
| Local approval gateway / intent freshness | E5.13 | Immutable intent snapshot and related checks exist; contract says gateway runtime remains blocked | PARTIAL / NOT END-TO-END |
| Adversarial rejection tests | E5.05-B, E5.05-C | Diagnostic PR #240 tests reproduce forged-authorization acceptance at the inspected base; existing tests cover some binding/lifecycle cases | DEFECT REPRODUCED; FIX NOT IMPLEMENTED |
| Exact commit CI and runtime evidence | E5.05-C | PR #240's diagnostic run is evidence of the defect on its tested head; no remediation commit exists to verify | NO FIX EVIDENCE |

## Concrete implementation blockers

1. **Trust-root governance:** identify who controls the owner signing key and how that authority is established outside the authorization object being verified.
2. **Protected key resolution:** provide a trusted, non-caller-injectable provider that maps issuer ID + key version to public verification material and lifecycle status.
3. **Production crypto provider:** select and declare an approved maintained implementation; do not silently promote HMAC test code or add an arbitrary dependency.
4. **Time and revocation:** specify authoritative inputs for validity windows and revocation/disablement.
5. **Runtime integration:** verify signature and every signed context field inside the protected execution boundary before consumption, retaining one transaction for consumption and state commit.
6. **Adversarial proof:** demonstrate invalid signature, unknown issuer/key version, revoked key, expiry/not-before, wrong scope/policy/evolution/parent/intent, replay, and caller-supplied-object forgery all fail before any consumption or state mutation.

## Safe next action

Do not modify production runtime until blockers 1–4 are grounded in an explicit authority/configuration contract. Once grounded, implement a narrow provider interface and verifier in a separate branch, add adversarial tests, then run exact-commit CI and audit persisted effects.

## Evidence ladder

- DESIGN: E5.05–E5.13 requirements exist; this matrix maps them to observed source boundaries.
- IMPLEMENTED: some intent/binding and test-only lifecycle components exist; production issuer proof does not.
- REACHABLE: production verifier path not established.
- RUNTIME: defect reproduced by diagnostic tests on PR #240's tested head; fixed runtime not established.
- PERSISTED: consumption/audit infrastructure exists, but forged-authorization acceptance shows it is not sufficient proof of authority.
- AUDITED: defect analysis exists; remediation has not been audited.
- CI_PROVEN: no remediation SHA exists to prove.


## SEQ 121 — minimal verifier boundary proposal

This section narrows implementation shape without choosing the still-unapproved real-world trust root or crypto provider.

### Proposed internal interface

- `AuthorizationProof`: immutable signed artifact containing a canonical payload and signature; no `owner_approved` boolean is accepted as proof.
- `TrustedKeyProvider`: configured inside the protected execution boundary. It resolves `(issuer_id, key_version)` to verification material plus authoritative status. Request objects cannot inject or replace this provider.
- `AuthorizationVerifier`: pure verification boundary receiving the proof and exact expected execution context, while obtaining keys, time and revocation state only through trusted dependencies configured outside the request.
- `VerifiedAuthorization`: verifier-produced result bound to the proof digest and exact context. It must not be constructible by request callers as a trusted capability; use module-private construction or a gate-owned opaque token pattern appropriate to the codebase.
- `require_trusted_execution`: invokes verification before `consume_authorization_in_transaction`. The commit adapter continues to own one transaction covering verification-dependent acceptance, consumption, candidate binding, and state persistence.

### Required verification order

1. Reject malformed/missing proof and unsupported protocol/algorithm.
2. Resolve issuer and exact key version through the configured trusted provider; reject unknown, disabled, expired or revoked key.
3. Verify domain-separated canonical payload signature.
4. Compare every signed claim against independently computed expected values: scope/action/audience, policy version and evidence digest, request provenance, evolution identity, parent state ID/digest, intent snapshot digest, validity window, authorization ID and nonce.
5. Check trusted time, authorization expiry/not-before, revocation and replay/consumption state.
6. Only after all checks succeed, proceed through existing Core invariants and atomic consumption/commit.

No consumption audit event may be appended on any rejection. Any exception after a tentative consumption write must roll back with the adapter transaction.

### Security tests required before integration is considered

- Direct construction of legacy `ExecutionAuthorization(owner_approved=True)` is rejected by the trusted gate.
- Caller-supplied `AuthorizationValidity` cannot substitute for independently verified claims.
- Invalid signature, malformed/non-canonical payload, wrong domain, unknown issuer/key version, unsupported algorithm, disabled/revoked key, not-yet-valid and expired proof are rejected.
- Wrong scope/action/audience/policy/evidence/provenance/evolution/parent/intent is rejected.
- Same authorization replay and cross-evolution replay are rejected.
- Every rejection asserts: no `execution.authorization.consume` event, no transition, no state mutation, and unchanged valid audit chain.
- Successful proof commits once; duplicate delivery is denied or handled only by an explicitly specified idempotency contract.
- Failure injection between consumption and persistence proves transaction rollback leaves the original durable graph intact.

### Explicit non-decisions

This proposal does not decide owner identity, signing-key custody, root distribution, algorithm/provider, trusted clock, revocation authority or delegation governance. Those must be supplied by an authoritative project decision/configuration contract. No generated default key, request-provided trust root, or test-only HMAC promotion is allowed.

### Acceptance sequence

1. Record the missing trust-governance decisions explicitly.
2. Implement provider/verifier on a separate branch only after those decisions are authoritative.
3. Add tests above before wiring verifier into the production gate.
4. Run exact-head CI; inspect the resulting run and failure counts.
5. Re-run the forged-authorization diagnostic against the candidate fix and verify both rejection and zero persisted side effects.
6. Independent audit; only then consider merging.
