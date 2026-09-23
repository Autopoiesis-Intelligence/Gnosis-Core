# E7.81 — Remediation Execution Authorization & Controlled Compensation Execution Contract

## Objective

Define the controlled execution boundary for an accepted remediation or compensation plan.

E7.81 converts an exact accepted E7.80 plan into a narrowly scoped execution authorization and controlled external execution attempt.

Authorization and execution remain separate records.

## Preconditions

Execution authorization MUST reference:

- exact E7.80 plan revision and digest;
- incident/resolution evidence;
- original execution evidence;
- accepted collaboration proposal/review where applicable;
- target resource;
- exact remediation action;
- authorized scope;
- privacy classification;
- required preconditions;
- executor identity.

## Authorization states

Authorization MUST use explicit states:

- ISSUED;
- ACTIVE;
- EXPIRED;
- REVOKED;
- CONSUMED;
- DENIED.

Only ACTIVE authorization may be used for execution.

A CONSUMED authorization MUST NOT be reused unless the contract explicitly defines bounded idempotency for the exact same execution identity.

## Action containment

Authorization MUST bind:

1. exact plan revision;
2. exact action class;
3. exact target resource;
4. exact permitted scope;
5. permitted payload/data class;
6. expected preconditions;
7. executor;
8. validity/revocation state.

No unspecified action, target, data class or side effect may be inferred.

## Compensation execution

Compensation MUST be executed as its declared action class.

The executor MUST NOT substitute an unrelated action merely because it appears capable of restoring a desired outcome.

If compensation requires a different action class or broader scope, execution MUST stop and a new governed plan/authorization path is required.

## Preconditions and fail-closed behavior

Execution MUST be denied when:

- plan is not ACCEPTED;
- authorization is not ACTIVE;
- plan revision differs;
- target differs;
- scope differs;
- required preconditions fail;
- authorization is expired/revoked;
- privacy classification is missing/conflicting;
- target state has diverged in a protected way;
- executor is outside authorized scope.

Unknown conditions resolve to DENY.

## Execution identity

Every execution attempt MUST have a unique execution identity.

A repeated request MAY be idempotent only when:

- execution identity is identical;
- target is identical;
- action and scope are identical;
- authorization remains valid;
- prior result is compatible with idempotent replay.

Conflicting replay MUST fail closed.

## Execution evidence

Every attempt MUST produce separate execution evidence referencing:

- exact authorization;
- exact plan revision;
- execution identity;
- target;
- action;
- scope;
- preconditions;
- observed result;
- target state before/after where available.

Execution evidence MUST NOT rewrite the plan or authorization history.

## Result handling

The executor MUST preserve explicit result classes:

- SUCCEEDED;
- FAILED;
- PARTIAL;
- UNKNOWN;
- REJECTED_BY_BOUNDARY.

No result may be upgraded to SUCCEEDED without new evidence.

Reconciliation follows E7.77.

## Revocation and recovery

Revocation MUST prevent future execution.

Restart/recovery MUST preserve:

- authorization state;
- revocation state;
- execution identities;
- execution evidence;
- consumed state.

Recovery MUST NOT resurrect an expired, revoked or consumed authorization.

## Privacy boundary

Only data explicitly permitted by the plan and authorization may cross the external execution boundary.

Private payloads MUST be rejected unless explicitly authorized.

## Authority separation

Plan acceptance != execution authorization
Execution authorization != execution
Execution != execution evidence
Execution evidence != Core authority

Successful compensation MUST NOT grant future authority or mutate Ψ-Core.

## Acceptance gate

E7.81 is satisfied only when implementation and tests demonstrate:

1. exact plan-to-authorization binding;
2. explicit authorization state machine;
3. action/target/scope containment;
4. fail-closed precondition checks;
5. unique execution identity;
6. conflicting replay rejection;
7. revocation and recovery integrity;
8. explicit result classes;
9. privacy enforcement;
10. separate execution evidence and reconciliation;
11. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.76 — Collaboration Execution Authorization & External Action Boundary
- E7.77 — External Collaboration Execution Evidence & Result Reconciliation
- E7.80 — Governed Remediation Plan & Compensation Authorization

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.81-r1
