# E7.76 — Collaboration Execution Authorization & External Action Boundary

## Objective

Define the fail-closed boundary between an accepted collaboration proposal and any external action such as GitHub publication, invitation, repository permission change, issue/PR creation, package transfer or other partner-facing operation.

E7.76 is an authorization contract. It does not itself perform an external action.

## Scope

An execution authorization MUST be derived from:

- an exact accepted E7.75 review record;
- the exact proposal revision;
- the requested action set;
- target resource(s);
- authorized scope;
- disclosure/privacy constraints;
- authorization subject;
- expiration/revocation state;
- required evidence and preconditions.

## Non-goals

Authorization MUST NOT:

- mutate Ψ-Core;
- change Core invariants;
- grant broader partner capabilities than the accepted proposal permits;
- infer authority from repository membership, proposal existence, registry presence or previous execution;
- expose private data;
- bypass GitHub/account security controls;
- authorize unspecified side effects.

## Required authorization record

The authorization record MUST bind:

1. accepted review identity/digest;
2. exact proposal revision;
3. target action class;
4. target resource identity;
5. authorized scope;
6. actor/executor identity;
7. authorization basis;
8. privacy/disclosure classification;
9. issuance revision/time or monotonic evidence ID;
10. expiry/revocation state;
11. required preconditions;
12. authorization digest.

## Action classes

Examples include:

- publish approved public material;
- create or update a public issue/PR;
- create a reviewed partner-facing package;
- send a collaboration invitation;
- change explicitly permitted repository metadata.

Each action class MUST have a separately defined resource and scope.

No wildcard action or wildcard resource may be inferred from a general collaboration acceptance.

## Fail-closed rules

Execution authorization MUST be denied when:

- the review is not ACCEPTED;
- the proposal revision differs from the accepted revision;
- the target resource differs from the authorized resource;
- requested scope exceeds accepted scope;
- required privacy evidence is absent or ambiguous;
- authorization is expired or revoked;
- the authorization is stale relative to a protected target revision;
- provenance is incomplete or conflicting;
- the executor is not within the authorized execution scope.

Unknown conditions resolve to DENY / NOT_AUTHORIZED.

## Replay and idempotency

Authorization is bound to an exact action/resource/proposal tuple.

A repeated identical execution request MAY be handled idempotently only when the stored authorization and execution identity match exactly.

A conflicting replay MUST fail closed.

Authorization reuse for a different resource, action, proposal revision or disclosure class is prohibited.

## Revocation and stale authorization

Revocation MUST remain effective after restart/recovery.

A valid authorization for an earlier target revision MUST NOT authorize a conflicting action after the protected target has advanced.

Recovery MUST NOT resurrect an authorization that was validly revoked before the recovered point.

## Separation of execution from authority

The authorization record does not itself execute an action.

External execution remains a separate adapter/boundary and MUST return explicit execution evidence.

The execution result does not retroactively expand authorization.

Execution evidence does not become Core authority.

## Privacy boundary

Only data explicitly classified as shareable under the accepted proposal and authorization may cross the external boundary.

Private or unknown-classification payloads MUST be rejected.

A public target does not make private source data public by default.

## Evidence requirements

For each attempted action, preserve enough evidence to reconstruct:

- accepted proposal/review;
- authorization revision;
- target and action;
- scope;
- executor;
- preconditions;
- allow/deny decision;
- execution result if an attempt occurred;
- resulting target revision/digest when available.

Evidence MUST distinguish authorization from execution outcome.

## Acceptance gate

E7.76 is satisfied only when implementation and tests demonstrate:

1. authorization cannot be issued from non-ACCEPTED review states;
2. exact proposal/review revision binding;
3. target/action/scope binding;
4. fail-closed unknown/stale/revoked behavior;
5. conflicting replay rejection;
6. restart/recovery revocation persistence;
7. privacy classification enforcement;
8. external execution remains a separate adapter;
9. exact-commit runtime/CI evidence.

Documentation is not runtime proof.

## Dependencies

- E7.30 — Partner Contract Acceptance & Capability Negotiation
- E7.46 — Governed Proposal Review / Acceptance Record
- E7.47 — Governed Execution / Controlled Contract Application Plan
- E7.48 — Controlled Execution Evidence / Mutation Receipt
- E7.74 — Self-Learning Collaboration Proposal Generator
- E7.75 — Governed Collaboration Proposal Review & Acceptance

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.76-r1
