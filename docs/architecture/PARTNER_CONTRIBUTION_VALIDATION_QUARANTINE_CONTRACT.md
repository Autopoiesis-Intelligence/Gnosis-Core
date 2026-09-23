# E7.24 — Partner Contribution Validation & Quarantine Contract

## Objective

Define the verification boundary between a submitted partner contribution and any learning/evidence surface that may consume it.

A contribution is untrusted until validation requirements are satisfied.

## Validation model

For contribution c and manifest M_p:

V(c,M_p) =
Identity
∧ SourceRevision
∧ Schema
∧ Integrity
∧ Provenance
∧ Scope
∧ Policy
∧ Freshness

Failure of any mandatory predicate MUST prevent promotion beyond quarantine.

## Validation stages

SUBMITTED
-> PARSED
-> IDENTITY_VALIDATED
-> SCHEMA_VALIDATED
-> INTEGRITY_VALIDATED
-> PROVENANCE_VALIDATED
-> SCOPE_VALIDATED
-> POLICY_VALIDATED
-> QUARANTINED
-> VERIFIED
-> ADMITTED

Quarantine is an isolation state, not an error deletion mechanism.

A failed validation MUST preserve the submitted material and failure evidence according to retention policy.

## Identity validation

The contribution MUST bind to a known PartnerIdentity and declared source.

A renamed repository, fork or substituted source revision MUST NOT silently inherit the original contribution identity or authority.

## Schema validation

The contribution and its manifest MUST conform to the applicable machine-readable schema.

Schema validity establishes structural validity only.

Schema validity does NOT establish:

- truth;
- trust;
- authority;
- semantic correctness;
- permission to modify Core.

## Integrity validation

Where a digest is supplied:

digest(payload) == declared_digest

MUST hold.

A mismatch MUST fail closed.

Integrity success proves content consistency with the declared digest, not truth of the content.

## Provenance validation

The validator MUST be able to reconstruct the applicable provenance chain:

Origin -> Source -> PartnerIdentity -> Manifest -> Contribution

Missing, contradictory or unverifiable provenance MUST prevent admission.

## Scope validation

Effective contribution scope MUST be independently derived.

S_granted(c) subseteq S_declared(p)

A contribution MUST NOT expand the partner's own scope.

Unknown or undeclared scope MUST be quarantined or rejected according to policy.

## Policy validation

The contribution MUST be checked against:

- explicit partner prohibitions;
- repository-level restrictions;
- data-class restrictions;
- current contract revision;
- revocation/suspension state;
- retention requirements;
- applicable security policy.

A revoked or suspended source MUST NOT produce newly admitted material.

## Freshness and revision binding

The validator MUST bind the contribution to the source revision and applicable manifest revision.

Stale or superseded manifests MUST NOT silently validate a newer source revision.

Revision mismatch is a validation event and MUST remain auditable.

## Failure behavior

Validation failures MUST NOT be converted into success through retry alone.

The system MUST preserve:

- contribution identity;
- validator decision;
- failed predicate;
- relevant source/manifest revisions;
- timestamp/event identity where available;
- provenance;
- prior status.

## Promotion boundary

Only verified material may proceed to admission:

Quarantined Contribution
-> Verification
-> Admission

There MUST be no direct:

PartnerContribution -> CoreState

and no:

PartnerContribution -> ExecutionAuthority

## Replay and idempotency

Replaying an identical valid contribution MUST be idempotent.

Replaying the same identity with different payload, provenance, source revision or manifest binding MUST fail closed.

A conflicting replay MUST NOT overwrite the original contribution or its validation history.

## Acceptance requirements

Future implementation MUST test:

1. unknown partner identity;
2. schema-invalid manifest;
3. malformed contribution;
4. digest mismatch;
5. broken provenance;
6. source revision mismatch;
7. stale manifest;
8. declared/granted scope mismatch;
9. prohibited data class;
10. revoked/suspended partner;
11. conflicting replay;
12. identical replay;
13. restart/recovery preserving quarantine;
14. no direct Core mutation;
15. no authority escalation.

## Status

DESIGNED / NOT_IMPLEMENTED.

No runtime validation capability is claimed until implementation and current evidence exist.
