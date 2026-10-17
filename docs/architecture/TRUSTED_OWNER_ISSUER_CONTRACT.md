# Trusted Owner Issuer Contract — Design Gate

**Status:** DESIGN / NOT IMPLEMENTED  
**Scope:** authorization boundary only. This document does not authorize production issuer implementation, schema changes, or changes to Core invariants.

## 1. Purpose

Define the minimum contract required before a trusted owner issuer can be integrated with the execution gate. Presence of an approval object, matching strings, an audit record, or a successful unit test is not proof of owner authority.

`ApprovalObject != VerifiedOwnerApproval != ExecutionAuthorization`

## 2. Required trust decisions

Implementation is blocked until the governance owner explicitly defines:

1. **Trust root:** which public key or other verifiable credential represents the owner authority, how it is provisioned, and who may rotate or revoke it.
2. **Credential format:** canonical encoding, supported signature algorithm, domain separation, issuer identity, key version, and signature verification rules.
3. **Scope model:** the exact action/domain scope that can be authorized and how scope attenuation is enforced.
4. **Validity policy:** expiry, revocation, freshness, and policy-version semantics. Do not invent a clock or implicit time source inside Core.
5. **Parent binding:** the exact parent-state identity and evolution identity that approval authorizes.
6. **Evidence semantics:** what `evidence_digest` commits to, how it is canonically computed, and which component verifies it.
7. **Replay policy:** unique authorization identity/nonce, durable one-time consumption, and how legitimate retries differ from replay.
8. **Key lifecycle:** unknown, retired, rotated, compromised, and revoked keys must have explicit outcomes. Never silently substitute a newer key.

These decisions are policy inputs, not details to infer from current string fields.

## 3. Proposed canonical payload (not yet an implementation schema)

The signed payload should bind, at minimum:

- protocol/domain identifier and payload version;
- issuer identity and key version;
- authority scope and scope version;
- policy version;
- exact evolution identity;
- exact parent-state identity/digest;
- request provenance;
- evidence digest and evidence type/version;
- unique authorization identity and nonce;
- validity bounds and revocation/credential reference;
- delegation reference and constraints, if delegation is supported.

Canonical serialization must be deterministic. Signatures must be domain-separated from unrelated protocols. A matching hash or identifier is not, by itself, proof of authority.

## 4. Issuance and execution sequence

```text
OwnerCredential
  -> VerifyCredentialAndSignature
  -> VerifyScopeAndPolicy
  -> VerifyExactIntentAndParent
  -> VerifyEvidenceBinding
  -> ConstructExecutionAuthorization
  -> ConstructAuthorizationValidity
  -> ExecutionGate
  -> ConsumeOnceInsideCommitTransaction
  -> PersistAuthorizedTransition
  -> VerifyPersistedResultAndAudit
```

Every rejection before commit must leave both the domain state and authorization-consumption record unchanged. If the transition fails after consumption but before commit, the enclosing transaction must roll consumption back. An unknown external outcome is not safely retried without an explicit idempotency/reconciliation policy.

## 5. Required fail-closed tests

| Case | Expected result |
|---|---|
| Valid trusted credential, exact intent and parent | May proceed to the existing execution gate |
| Missing/invalid signature or unsupported algorithm | Reject before consumption and mutation |
| Unknown, revoked or disallowed key version | Reject; no fallback to latest key |
| Wrong scope, policy, evolution, provenance or parent | Reject before consumption and mutation |
| Evidence digest absent or mismatched | Reject before consumption and mutation |
| Expired or revoked authorization | Reject before consumption and mutation |
| Same authorization consumed twice | Second attempt rejects |
| Downstream commit failure | Consumption and state mutation roll back together |
| Restart after consumed/revoked state | Must not resurrect executable authority |
| Canonical payload ambiguity or cross-protocol reuse | Reject |

Each end-to-end test must assert the durable state, consumption event, and audit chain after reopening the database, not only an exception or in-memory flag.

## 6. Current integration gap

The current `TrustedOwnerIssuer.issue()` checks configured root/scope/policy values and requires a non-empty evidence digest, but returns an `ExecutionAuthorization` without `policy_version` and `validity_evidence_digest`. The execution gate requires both fields. Separately, `OwnerApproval` is a string-valued data object; field equality does not cryptographically authenticate the owner.

Therefore the current issuer output is not end-to-end usable by the gate as-is, and the existing string checks do not close the owner-authenticity requirement. Do not patch this by copying caller-supplied strings into the missing fields.

## 7. Explicit non-goals

This design does not:
- implement or claim a production trusted issuer;
- establish the real-world identity of an owner;
- add a clock, global selector, external LLM, or hidden authority to Ψ-Core;
- store private keys in source or ordinary audit payloads;
- authorize schema/migration changes;
- turn test/development credentials into production authority.

## 8. Acceptance gates

The issuer work may leave DESIGN only after all of the following are independently reviewable:

- trust root, credential, scope and revocation semantics are approved;
- canonical payload and signature verification are implemented;
- issuer output binds the same verified policy/evidence/intent used by the gate;
- positive and adversarial end-to-end tests cover the table above;
- exact commit SHA has successful required CI and review evidence;
- runtime and post-restart evidence demonstrate no mutation on rejection and no resurrection/replay.

**Status remains DESIGN / NOT IMPLEMENTED until those gates are proven on an exact commit.**
