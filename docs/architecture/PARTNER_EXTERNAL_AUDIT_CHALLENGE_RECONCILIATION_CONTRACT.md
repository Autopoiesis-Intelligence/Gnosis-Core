# E7.87 — External Audit Challenge, Dispute & Evidence Reconciliation Contract

## Objective

Define the governed process for handling an external auditor challenge, dispute or discrepancy concerning exported evidence, provenance, verification or attestation.

A challenge is an evidence/governance event. It does not grant the challenger authority to mutate source records, Ψ-Core, permissions or historical evidence.

## Preconditions

A challenge MUST reference:

- exact audit package identity/digest;
- exact verification or attestation identity where applicable;
- challenged evidence item(s);
- challenger identity;
- challenge scope;
- stated basis;
- relevant disclosure classification;
- applicable challenge/reconciliation policy revision.

## Challenge states

A challenge MUST use explicit states:

- FILED;
- ACKNOWLEDGED;
- INVESTIGATING;
- EVIDENCE_REQUESTED;
- RECONCILING;
- RESOLVED;
- REJECTED;
- WITHDRAWN;
- ESCALATED;
- CLOSED.

A challenge state MUST NOT imply execution or governance authority.

## Challenge record

The record MUST bind:

1. challenge identity/digest;
2. challenged package/evidence/attestation;
3. challenger identity;
4. exact disputed claim or relationship;
5. supporting basis supplied by the challenger;
6. internal evidence references;
7. investigation/reconciliation actions;
8. resolution state;
9. resolution rationale;
10. verifier/resolver identity;
11. limitations and unresolved uncertainty;
12. revision/provenance.

## Reconciliation rules

Reconciliation MUST compare the disputed claim against the authoritative internal evidence available for the challenged scope.

Possible outcomes MUST distinguish at least:

- INTERNAL_EVIDENCE_SUPPORTED;
- INTERNAL_EVIDENCE_CONTRADICTED;
- EVIDENCE_INCOMPLETE;
- EVIDENCE_CONFLICT;
- SCOPE_MISMATCH;
- UNRESOLVED.

The system MUST NOT alter authoritative evidence merely to satisfy a challenge.

## New evidence

Additional evidence MAY be requested or supplied only within the applicable disclosure policy.

New evidence MUST receive:

- source identity;
- provenance;
- classification;
- acquisition/receipt evidence;
- integrity identity/digest;
- relationship to the disputed claim.

Private evidence MUST NOT become public/common evidence merely because it was requested during a challenge.

## Attestation impact

Where a challenge materially affects an attestation:

- mark the affected attestation as under challenge where policy supports such a state;
- preserve the original attestation;
- issue a qualified/superseding/withdrawal record only through the governed attestation process.

A challenge MUST NOT directly mutate or delete an attestation.

## Conflict handling

If internal and external evidence conflict:

- preserve both claims;
- identify the conflict;
- identify the evidence currently relied upon and its basis;
- record unresolved uncertainty;
- prevent silent normalization.

A conflict may remain unresolved.

## Escalation

ESCALATED means additional governance, evidence or review is required.

Escalation MUST NOT bypass:

- privacy controls;
- disclosure scope;
- authorization boundaries;
- evidence immutability;
- Ψ-Core authority boundaries.

## Authority separation

Challenge != evidence mutation
Challenge != authorization
Challenge != execution
Reconciliation != Core mutation
Dispute resolution != history deletion

No external challenger may directly write authoritative internal state.

## Privacy boundary

Challenge handling MUST use minimum necessary disclosure.

Any expanded disclosure requires separate authorization.

Challenge artifacts MUST avoid reproducing private payloads unnecessarily.

## Recovery and replay

Challenge state and reconciliation evidence MUST survive restart/recovery.

Identical challenge submission MAY be idempotent when identity and scope are identical.

Conflicting replay MUST fail closed.

Historical challenge records MUST remain reconstructable.

## Acceptance gate

E7.87 is satisfied only when implementation and tests demonstrate:

1. explicit challenge state machine;
2. exact challenged-artifact binding;
3. scoped evidence reconciliation;
4. preservation of internal evidence;
5. controlled additional-evidence intake;
6. explicit conflict outcomes;
7. attestation impact separation;
8. no external mutation authority;
9. privacy enforcement;
10. recovery/replay integrity;
11. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.85 — Collaboration Evidence Export & External Audit Package
- E7.86 — External Auditor Verification & Attestation Boundary
- E7.79 — Governed External Collaboration Incident & Conflict Resolution
- E7.84 — Lifecycle Retention, Evidence Preservation & Controlled Data Disposal

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.87-r1
