# E7.79 — Governed External Collaboration Incident & Conflict Resolution Contract

## Objective

Define the governed process for resolving conflicts, incidents, UNKNOWN outcomes, scope mismatches and recovery findings produced by external collaboration execution.

Resolution is a recorded decision process. It is not an automatic repair, retry, compensation, authorization escalation or history rewrite.

## Resolution inputs

A resolution record MUST reference:

- exact incident/conflict evidence;
- exact execution evidence;
- authorization and accepted review;
- proposal revision;
- target resource and scope;
- observed state;
- relevant privacy classification;
- detected conflict or failure class;
- required resolution decision.

## Resolution states

A resolution MUST use an explicit state:

- OPEN;
- INVESTIGATING;
- RESOLVED;
- REJECTED;
- DEFERRED;
- ESCALATED;
- CLOSED_WITHOUT_ACTION.

A resolution state MUST NOT imply execution authority.

## Required resolution record

The record MUST bind:

1. incident/conflict identity and digest;
2. source evidence identities/digests;
3. exact proposal/review/authorization chain;
4. target and action scope;
5. observed conflicting state;
6. resolution state;
7. decision reason;
8. resolver identity;
9. required follow-up action class, if any;
10. privacy/disclosure classification;
11. revision and provenance;
12. resolution digest.

## Decision separation

The following boundaries are mandatory:

Incident detection != Incident resolution
Resolution decision != Execution authorization
Resolution decision != Execution
Resolution != Evidence rewrite
Resolution != Core authority

A resolution record MUST NOT silently authorize a new external action.

## Conflict resolution

When evidence conflicts:

- preserve all original evidence;
- record the conflict explicitly;
- identify the conflicting claims;
- identify which evidence is currently relied upon and why;
- record unresolved uncertainty where present;
- never delete or overwrite the conflicting record.

A conflict may remain unresolved.

## UNKNOWN resolution

UNKNOWN may be resolved only by new evidence sufficient to distinguish the external state.

A resolution MUST NOT infer success or failure merely from absence of error.

Any external state query MUST use its own valid authorization and execution evidence.

## Scope mismatch

A scope mismatch MUST remain a security-relevant incident.

Resolution may classify the mismatch, quarantine affected evidence, or request governed remediation.

Resolution MUST NOT retroactively make unauthorized scope authorized.

## Escalation

ESCALATED is a state, not authority.

Escalation MUST preserve the complete evidence chain and identify the missing decision, authority or evidence required for further action.

No escalation path may bypass privacy, governance or Core boundaries.

## Remediation and compensation

If remediation, retry, rollback or compensation is required, the resolution record MUST reference the separate authorization and execution contracts governing that action.

A resolution record alone cannot execute or authorize remediation.

## Privacy boundary

Resolution records MUST minimize private payload exposure.

Sensitive/private evidence should be represented by references, digests and authorized abstractions where sufficient.

An incident does not create a disclosure exception.

## Recovery and replay

Resolution state MUST survive restart/recovery.

A conflicting replay MUST fail closed.

Historical resolution records MUST remain immutable; superseding decisions create new revisions linked to prior records.

## Acceptance gate

E7.79 is satisfied only when implementation and tests demonstrate:

1. explicit incident/conflict state machine;
2. complete provenance linkage;
3. preservation of conflicting evidence;
4. no implicit authorization from resolution;
5. UNKNOWN resolution only from sufficient new evidence;
6. scope mismatch cannot be retroactively authorized;
7. separate remediation authorization;
8. restart/recovery integrity;
9. conflicting replay rejection;
10. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.77 — External Collaboration Execution Evidence & Result Reconciliation
- E7.78 — External Collaboration Failure, Compensation & Recovery Boundary
- E7.76 — Collaboration Execution Authorization & External Action Boundary

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.79-r1
