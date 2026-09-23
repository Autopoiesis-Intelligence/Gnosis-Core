# E7.80 — Governed Remediation Plan & Compensation Authorization Contract

## Objective

Define the governed boundary for creating a remediation or compensation plan after an external collaboration incident has been resolved or explicitly authorized for remediation.

A remediation plan is a declarative, bounded proposal. It does not execute actions, mutate Core, grant permissions or authorize unspecified side effects.

## Preconditions

A remediation plan MUST reference:

- exact incident/conflict resolution;
- exact execution evidence;
- original authorization;
- accepted proposal/review;
- target resource and affected scope;
- observed failure/conflict state;
- remediation objective;
- privacy classification;
- required evidence.

A plan MUST NOT be created from an unresolved or missing incident chain unless an explicit governance rule permits a remediation investigation state.

## Plan states

A remediation plan MUST use an explicit state:

- PROPOSED;
- VALIDATED;
- ACCEPTED;
- REJECTED;
- DEFERRED;
- EXPIRED;
- REVOKED;
- COMPLETED;
- FAILED.

ACCEPTED means the plan passed its governance gate. It does not mean execution occurred.

## Required plan record

The record MUST bind:

1. incident/resolution identity and digest;
2. execution evidence identity;
3. original authorization identity;
4. exact proposal revision;
5. target resource;
6. affected scope;
7. remediation/compensation action class;
8. intended outcome;
9. privacy/disclosure classification;
10. preconditions;
11. validation evidence;
12. reviewer/authorizer identity;
13. plan revision;
14. plan digest.

## Scope containment

A remediation plan MUST be no broader than the affected and authorized scope unless a new governed proposal explicitly expands the scope.

The plan MUST enumerate:

- target resources;
- allowed action classes;
- excluded resources;
- excluded data;
- expected state transition;
- required verification evidence.

Wildcards and implicit scope expansion are prohibited.

## Compensation separation

Compensation MUST be treated as a distinct action class from ordinary retry.

A compensation plan MUST identify:

- the failed/partial/unknown action;
- the reason compensation is required;
- the intended compensating effect;
- conditions under which compensation is safe;
- evidence required to confirm the result.

A compensation plan cannot authorize itself.

## Authorization boundary

Execution requires a separate authorization record referencing the exact accepted plan.

Plan acceptance MUST NOT grant:

- GitHub permissions;
- partner capabilities;
- publication rights;
- repository administration rights;
- Core mutation authority;
- authority over unrelated resources.

## Fail-closed rules

Plan creation or acceptance MUST fail closed when:

- incident provenance is incomplete;
- resolution is stale/revoked where required;
- target identity is ambiguous;
- privacy classification is missing;
- action exceeds affected scope;
- required validation evidence is absent;
- plan conflicts with an existing unresolved authorization;
- replay produces conflicting plan identity.

## Replay and revision

A changed incident, resolution, target or action MUST create a new plan revision.

An accepted plan MUST NOT silently inherit acceptance after material changes.

Conflicting replay MUST fail closed.

Historical plans MUST remain reconstructable.

## Execution and result boundary

The plan does not execute.

Execution MUST use:

- a separate execution authorization;
- a separate execution attempt identity;
- separate execution evidence;
- reconciliation against the actual target state.

A successful remediation does not erase the original incident.

## Privacy boundary

Remediation records MUST minimize private payloads.

Private partner/user data MUST NOT be copied into common remediation artifacts unless explicitly authorized.

A remediation need does not create a disclosure exception.

## Recovery

Restart/recovery MUST preserve:

- plan state;
- authorization linkage;
- execution history;
- incident linkage;
- revocation state.

Recovery MUST NOT resurrect expired or revoked plans.

## Acceptance gate

E7.80 is satisfied only when implementation and tests demonstrate:

1. exact incident/resolution provenance;
2. explicit plan state machine;
3. scope containment;
4. compensation separated from retry;
5. acceptance does not authorize execution;
6. stale/revoked/conflicting plan rejection;
7. privacy enforcement;
8. recovery integrity;
9. exact plan-to-authorization binding;
10. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.78 — External Collaboration Failure, Compensation & Recovery Boundary
- E7.79 — Governed External Collaboration Incident & Conflict Resolution
- E7.76 — Collaboration Execution Authorization & External Action Boundary
- E7.77 — External Collaboration Execution Evidence & Result Reconciliation

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.80-r1
