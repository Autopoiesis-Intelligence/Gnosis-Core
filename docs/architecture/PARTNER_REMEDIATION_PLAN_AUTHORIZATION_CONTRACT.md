# E7.92 — Remediation Plan Authorization Boundary Contract

## Objective

Define the governed boundary between an E7.91 accepted remediation plan and authorization to execute that plan.

Authorization MUST be explicit, exact-scoped, time-bounded and independently reconstructable. Plan acceptance alone MUST NOT authorize execution.

## Preconditions

Authorization MUST reference:

- exact accepted plan identity and revision;
- E7.91 validation identity;
- originating finding and governance decision;
- exact target/resource;
- exact permitted actions;
- prohibited actions;
- execution actor/identity;
- validity window;
- required verification criteria;
- applicable authorization policy revision;
- privacy/security constraints.

## Authorization states

An authorization MUST use explicit states:

- REQUESTED;
- VALIDATING;
- APPROVED;
- REJECTED;
- BLOCKED;
- EXPIRED;
- REVOKED;
- CONSUMED;
- SUPERSEDED.

APPROVED means authorization exists within the declared scope and validity window. It does not prove execution occurred.

## Exact scope

Authorization MUST bind:

1. plan identity/revision;
2. target/resource identity;
3. permitted operation(s);
4. prohibited operation(s);
5. execution actor;
6. maximum scope;
7. validity start/end;
8. required preconditions;
9. required postconditions;
10. verification criteria;
11. authorization identity/revision.

Wildcard authorization MUST NOT be permitted where exact scope can be expressed.

## Least authority

The authorization MUST grant no capability beyond the accepted plan.

Authorization MUST NOT implicitly grant:

- repository administration;
- unrelated data access;
- disclosure rights;
- compensation authority beyond explicitly declared scope;
- permanent capability;
- Ψ-Core mutation authority.

Any additional action requires a separate governed authorization.

## Preconditions and invalidation

Execution MUST be blocked when:

- plan acceptance is missing or superseded;
- authorization is expired or revoked;
- target identity changed;
- required preconditions are unsatisfied;
- applicable policy revision invalidates the authorization;
- conflicting authorization exists;
- required security/privacy condition is unknown.

Unknown critical authorization conditions MUST fail closed.

## Validity and consumption

An authorization MAY be:

- single-use;
- bounded-use;
- time-bounded.

Consumption MUST produce evidence.

A consumed single-use authorization MUST NOT be reused.

Expiration or revocation MUST NOT erase historical authorization evidence.

## Revocation

REVOCATION MUST:

- identify the authorization;
- identify effective time;
- identify reason;
- preserve prior authorization state;
- prevent future execution within revoked scope.

Revocation MUST NOT claim that previously executed operations were undone.

## Execution separation

Authorization != execution
Authorization != execution success
Authorization != verification
Verification != authorization

Execution must produce separate evidence under the applicable execution contract.

## Emergency path

Emergency execution, if supported, MUST use a separate explicit authorization path with:

- emergency basis;
- exact scope;
- authority;
- validity window;
- mandatory post-execution review.

Emergency status MUST NOT silently expand scope.

## Conflict handling

If two active authorizations conflict:

- preserve both records;
- identify conflicting scope;
- block ambiguous execution;
- route to governed resolution.

The system MUST NOT silently select an authorization.

## Privacy and security

Authorization records MUST minimize sensitive data.

Secrets MUST NOT be embedded when a reference/capability mechanism is sufficient.

Authorization does not itself authorize disclosure of private payloads unless explicitly declared.

## Recovery and replay

Authorization state MUST survive restart/recovery.

Identical authorization requests MAY be idempotent when plan revision, scope, actor, validity and policy revision are identical.

Conflicting replay MUST fail closed.

Historical authorization records MUST remain reconstructable.

## Acceptance gate

E7.92 is satisfied only when implementation and tests demonstrate:

1. exact plan-to-authorization provenance;
2. explicit authorization state machine;
3. exact target/action binding;
4. least-authority enforcement;
5. validity-window enforcement;
6. precondition/invalidation checks;
7. single-use/bounded-use consumption;
8. revocation integrity;
9. execution separation;
10. emergency-path separation;
11. conflict fail-closed behavior;
12. recovery/replay integrity;
13. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.91 — Remediation Plan Validation & Acceptance Gate
- E7.80 — Governed Remediation Plan & Compensation Authorization
- E7.81 — Remediation Execution Authorization & Controlled Compensation Execution
- E7.82 — Remediation Result Verification & Governed Closure

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.92-r1
