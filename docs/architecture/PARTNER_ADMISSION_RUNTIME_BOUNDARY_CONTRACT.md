# E7.26 — Partner Admission Runtime Boundary Contract

## Objective

Define the runtime gate by which a validated partner contribution may become an admitted learning/evidence object without acquiring Core mutation or execution authority.

## Admission predicate

For contribution c:

Admit(c) =
Validated(c)
∧ ProvenanceBound(c)
∧ ScopeAllowed(c)
∧ PolicyAllowed(c)
∧ NotRevoked(c)
∧ IntegrityCurrent(c)

Admission MUST be fail-closed.

No missing predicate may be interpreted as true.

## State transition

The reference transition is:

QUARANTINED
-> VALIDATED
-> ADMISSION_REVIEW
-> ADMITTED

Possible terminal/non-admitted outcomes:

REJECTED
REVOKED
QUARANTINED

A contribution MUST NOT transition directly:

SUBMITTED -> ADMITTED

or:

PARTNER -> CORE_STATE

## Runtime boundary

The admission component MUST be separated from:

- partner identity declaration;
- manifest parsing;
- validation;
- provenance recording;
- Core evolution;
- execution authorization.

Admission consumes verified evidence and emits an admitted learning/evidence record.

It does NOT emit Core mutation authority.

## Admission record

An admission event SHOULD contain:

- contribution_id;
- partner_identity;
- source_revision;
- manifest_revision;
- provenance reference;
- validation result reference;
- scope decision;
- policy decision;
- admission decision;
- exact contract revision;
- actor/system context;
- event identifier;
- timestamp where runtime policy requires it.

The admission event MUST be append-only/auditable under the project's existing audit boundary.

## Scope isolation

Admission scope MUST be explicitly represented.

The runtime MUST NOT infer broader permissions from:

- partner identity;
- repository membership;
- manifest presence;
- prior admissions;
- contribution type;
- successful validation.

Each admission is bounded by its own evaluated scope.

## No authority escalation

Admission MUST NOT create:

- execution authority;
- Core write authority;
- governance authority;
- policy-edit authority;
- contract-edit authority;
- authority to admit other contributions.

Formally:

Admitted(c) != AuthorizedActor(p)

and:

AdmissionEvent(c) != CoreMutation(c)

## Core boundary

The admitted object may enter the learning/evidence layer:

Partner Contribution
-> Validation
-> Provenance
-> Admission
-> Learning Evidence

To affect canonical Core behavior, a separate existing path MUST be used:

Learning Evidence
-> Candidate / RuleProposal
-> Verification / Shadow Evaluation
-> Governance
-> Protected Core transition

There MUST be no implicit shortcut from admission to Core mutation.

## Revocation and post-admission state

Revocation MUST be independently evaluable after admission.

A previously admitted contribution may become:

ACTIVE
-> SUSPENDED
-> REVOKED

without deleting historical admission evidence.

Consumers MUST check current validity where policy requires it rather than assuming historical admission is permanently valid.

## Idempotency

Repeated admission of the same contribution under the same applicable contract/provenance/scope decision MUST be idempotent.

A conflicting admission request MUST fail closed and MUST NOT create a second authoritative history for the same contribution identity.

## Failure safety

Any runtime failure before durable admission MUST NOT leave a partially authoritative admission.

The implementation MUST use the existing persistence/audit transaction boundary where applicable.

After restart, the system MUST resolve to one of:

- not admitted;
- fully admitted;
- explicitly quarantined/rejected.

No ambiguous half-admitted state may be treated as authoritative.

## Acceptance requirements

Implementation MUST eventually test:

1. valid contribution admission;
2. missing validation;
3. broken provenance;
4. revoked source;
5. scope escalation;
6. policy denial;
7. stale contract revision;
8. duplicate admission;
9. conflicting admission;
10. crash before commit;
11. crash after commit;
12. restart recovery;
13. no Core mutation;
14. no authority escalation;
15. revocation after admission;
16. audit/provenance preservation.

## Status

DESIGNED / NOT_IMPLEMENTED.

This contract does not claim runtime admission capability until implementation and reproducible verification exist.
