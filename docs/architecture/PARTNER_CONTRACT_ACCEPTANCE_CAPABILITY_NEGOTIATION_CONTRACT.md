# E7.30 — Partner Contract Acceptance & Capability Negotiation Contract

## Objective

Define how an invited partner explicitly accepts, rejects, or requests changes to a contract package and how the resulting capability set is recorded without allowing acceptance to escalate authority.

## Acceptance record

For partner p and package K:

A(p,K) = (partner_identity, package_id, package_digest, accepted_contracts, rejected_contracts, requested_changes, effective_scope, acceptance_revision, evidence)

The acceptance record MUST bind to the exact package identity and digest.

## Explicit acceptance

A contract is effective for the partner only when:

- the package is valid and current;
- the partner identity is bound;
- the applicable contract revision is identified;
- acceptance is explicit;
- required evidence/attestation exists;
- the resulting scope is permitted by Core policy.

Silence, package receipt or successful import MUST NOT be interpreted as acceptance.

## Rejection and partial acceptance

A partner MAY reject individual contracts or request changes where policy permits.

Partial acceptance MUST NOT cause unaccepted contracts to become effective.

Requested changes create a new negotiation state and MUST NOT mutate the existing contract revision.

## Capability negotiation

For declared partner capabilities C_declared and policy-allowed capabilities C_policy:

C_effective ⊆ C_declared ∩ C_policy

Acceptance may select a subset of policy-allowed capabilities.

A partner cannot obtain a capability solely by requesting or accepting it.

## Capability versus authority

Capability describes an allowed interaction or contribution class.

Authority is separately governed.

Therefore:

AcceptedCapability(p,c) != ExecutionAuthority(p)

AcceptedCapability(p,c) != CoreWriteAuthority(p)

AcceptedCapability(p,c) != GovernanceAuthority(p)

## Contract changes

A requested contract modification MUST produce a new contract revision or a formally governed amendment.

The partner acceptance of revision n MUST NOT silently apply to revision n+1.

When a new revision changes obligations or scope, a new acceptance decision may be required.

## Evidence and provenance

Acceptance MUST preserve:

- partner identity;
- package identity/digest;
- exact contract revisions;
- scope decision;
- capability decision;
- evidence/attestation references;
- acceptance event identity;
- applicable registry revision.

Acceptance provenance MUST be independently auditable.

## Expiry and revocation

An acceptance MAY expire or be revoked according to contract policy.

Expiration/revocation changes current applicability without deleting the historical acceptance event.

Historical acceptance != current permission.

## No self-escalation

A partner MUST NOT use an acceptance record, negotiated capability or package import to:

- grant itself new capabilities;
- grant another partner authority;
- alter Core policy;
- alter contract governance;
- bypass admission;
- modify the registry as an authority root.

## Determinism and conflict handling

For a fixed package, partner identity, policy revision and explicit acceptance record, the effective capability set MUST be deterministic.

Conflicting acceptance records MUST be resolved by an explicit governance rule; they MUST NOT be merged by arbitrary last-writer-wins behavior.

## Acceptance requirements

Implementation MUST eventually test:

1. explicit acceptance;
2. receipt without acceptance;
3. partial acceptance;
4. rejection;
5. requested contract change;
6. capability outside policy;
7. capability outside declared scope;
8. package digest mismatch;
9. stale package;
10. acceptance against wrong contract revision;
11. acceptance expiry;
12. revocation;
13. conflicting acceptance records;
14. restart/recovery;
15. no authority escalation.

## Status

DESIGNED / NOT_IMPLEMENTED.

This contract specifies negotiation and acceptance semantics only. It does not claim runtime partner negotiation capability.
