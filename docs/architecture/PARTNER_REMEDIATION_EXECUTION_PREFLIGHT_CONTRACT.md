# E7.93 — Remediation Execution Admission & Preflight Gate Contract

## Objective

Define the final admission boundary immediately before remediation execution.

The preflight gate verifies that an already authorized operation may enter execution under its exact current conditions. Preflight MUST NOT execute the operation, expand authority or mutate Ψ-Core.

## Preconditions

Preflight MUST reference:

- exact accepted remediation plan revision;
- exact authorization identity/revision;
- target/resource identity;
- permitted operation;
- execution actor;
- validity window;
- required preconditions;
- current resource state required for admission;
- required verification criteria;
- applicable policy revision;
- active conflict/hold state.

## Admission states

A preflight MUST use explicit states:

- REQUESTED;
- CHECKING;
- ADMITTED;
- REJECTED;
- BLOCKED;
- EXPIRED;
- REVOKED;
- STALE;
- CONFLICTED.

ADMITTED means the operation passed preflight for the declared execution context. It does not mean execution occurred.

## Required checks

The gate MUST verify at minimum:

1. authorization exists and is valid;
2. authorization scope exactly matches requested operation;
3. plan revision is still accepted;
4. target/resource identity matches;
5. validity window is active;
6. required preconditions are satisfied;
7. required holds/conflicts are absent or explicitly resolved;
8. actor identity is permitted;
9. privacy/security conditions are satisfied;
10. required execution dependencies are available;
11. no superseding plan/authorization invalidates the operation;
12. required verification path exists.

Unknown critical conditions MUST result in BLOCKED or STALE.

## Resource-state binding

Where execution depends on mutable resource state, preflight MUST bind the state used for admission.

If the relevant state changes after preflight and before execution, the admission MUST be treated as STALE unless the authorization explicitly permits that state transition.

The system MUST NOT assume that a previously valid preflight remains valid indefinitely.

## Exact operation binding

Preflight MUST compare the actual requested operation against:

- target;
- action;
- parameters;
- scope;
- actor;
- authorization.

Any mismatch MUST fail closed.

The gate MUST NOT silently normalize or broaden the requested operation.

## Holds and conflicts

Execution MUST be blocked when an active:

- legal/security hold;
- governance block;
- privacy restriction;
- conflicting authorization;
- conflicting remediation;
- target lock;

affects the requested operation and has not been explicitly resolved.

## Admission evidence

Every ADMITTED or rejected preflight MUST produce evidence containing:

- plan identity/revision;
- authorization identity/revision;
- target/resource;
- requested operation;
- actor;
- relevant resource-state identity;
- checks performed;
- result;
- policy revision;
- admission identity;
- ordering/timestamp evidence where available.

ADMITTED evidence MUST NOT be treated as execution evidence.

## TOCTOU protection

Where practical, the execution handoff MUST bind the admitted state to the actual execution start.

If the state changes between check and execution start, the system MUST revalidate or fail closed.

A successful preflight MUST NOT be used as proof that the later execution remained authorized.

## Emergency execution

Emergency execution MUST still pass the applicable emergency preflight requirements.

Emergency status MUST NOT bypass exact scope, actor, validity or required safety/privacy conditions unless a separate explicitly governed emergency policy permits the deviation.

Any permitted deviation MUST be recorded.

## Recovery and replay

Preflight state and evidence MUST survive restart/recovery.

Identical preflight requests MAY be idempotent when authorization, plan revision, target, operation, actor and bound resource state are identical.

Conflicting replay MUST fail closed.

An ADMITTED preflight MUST NOT automatically replay execution.

## Authority separation

Preflight != execution
Preflight != authorization
Preflight != execution success
Preflight != verification
Preflight != Core mutation

## Acceptance gate

E7.93 is satisfied only when implementation and tests demonstrate:

1. exact authorization-to-preflight binding;
2. complete preflight checks;
3. exact operation comparison;
4. mutable-state binding;
5. hold/conflict blocking;
6. actor validation;
7. TOCTOU protection;
8. separate admission evidence;
9. emergency-path controls;
10. replay/recovery integrity;
11. no automatic execution from admission;
12. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.92 — Remediation Plan Authorization Boundary
- E7.91 — Remediation Plan Validation & Acceptance Gate
- E7.81 — Remediation Execution Authorization & Controlled Compensation Execution
- E7.82 — Remediation Result Verification & Governed Closure

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.93-r1
