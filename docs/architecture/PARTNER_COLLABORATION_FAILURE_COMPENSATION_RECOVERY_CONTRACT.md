# E7.78 — External Collaboration Failure, Compensation & Recovery Boundary

## Objective

Define the fail-closed handling of FAILED, PARTIAL, UNKNOWN, REJECTED or MISMATCH outcomes from external collaboration execution.

E7.78 separates observation of failure from any retry, compensation, remediation or recovery action.

This contract does not authorize retry, execute compensation, rewrite evidence, mutate Ψ-Core, broaden partner scope, or conceal an external failure.

## Failure classes

External execution MUST preserve the observed class:

- FAILED;
- PARTIAL;
- UNKNOWN;
- REJECTED_BY_BOUNDARY;
- MISMATCH.

The system MUST NOT normalize these states into success.

## Required failure record

A failure/recovery record MUST bind:

1. exact execution evidence identity/digest;
2. authorization identity/digest;
3. accepted review identity/digest;
4. proposal revision;
5. action and target;
6. observed failure/result class;
7. observed target state;
8. detected invariant/scope/provenance mismatch where applicable;
9. recovery assessment;
10. next permitted action class;
11. reviewer/authority reference when a governed decision is required;
12. record revision/digest.

## Compensation boundary

Compensation is a separate governed action.

A failure record MUST NOT itself authorize:

- retry;
- rollback;
- compensating transaction;
- repository modification;
- permission change;
- partner notification;
- Core mutation.

Any compensation plan MUST reference the exact failure evidence and receive its own authorization.

## Retry rules

Automatic retry is prohibited unless an explicit contract authorizes it.

A retry MUST:

- create a new execution-attempt identity;
- reference the previous attempt;
- use a currently valid authorization;
- revalidate target and scope;
- preserve the previous result;
- generate independent execution evidence.

A failed attempt MUST NOT be overwritten by a retry result.

## UNKNOWN handling

UNKNOWN means that the external outcome cannot be established from available evidence.

UNKNOWN MUST remain unresolved until new evidence establishes a different state.

Recovery MUST NOT assume either success or failure when the external state is genuinely unknown.

Where a target-state query is available, it MUST be separately authorized and evidenced.

## PARTIAL handling

PARTIAL means that execution produced an incomplete or mixed result.

The system MUST identify known completed and incomplete portions where evidence permits.

The remaining action MUST NOT be inferred automatically.

Any continuation or compensation requires separate scope and authorization.

## Recovery rules

Recovery MUST be deterministic with respect to the recorded evidence and current authorization state.

Recovery MUST:

- preserve all prior evidence;
- detect stale/revoked authorization;
- detect target divergence;
- prevent scope expansion;
- preserve privacy constraints;
- fail closed on ambiguous state.

Recovery MUST NOT silently repair or rewrite historical records.

## Conflict handling

If external state conflicts with recorded evidence:

- create a conflict finding;
- preserve the original evidence;
- record the observed conflicting state;
- prevent automatic reconciliation to success;
- require governed resolution where action is needed.

Conflict resolution MUST NOT erase the fact that a conflict occurred.

## Privacy boundary

Failure, recovery and compensation records MUST avoid copying private payloads unnecessarily.

Unknown or private data MUST NOT cross the common collaboration boundary merely because an incident occurred.

## Authority separation

Failure evidence != recovery decision
Recovery decision != compensation authorization
Compensation authorization != compensation execution
Execution result != Core authority

No failure path may become an authority escalation path.

## Acceptance gate

E7.78 is satisfied only when implementation and tests demonstrate:

1. preservation of FAILED/PARTIAL/UNKNOWN/MISMATCH states;
2. no implicit retry;
3. new identity for authorized retries;
4. separate authorization for compensation;
5. UNKNOWN remains unresolved without evidence;
6. PARTIAL does not become full success;
7. conflict evidence is append-only;
8. recovery survives restart without history rewrite;
9. privacy boundary remains enforced;
10. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.47 — Governed Execution / Controlled Contract Application Plan
- E7.48 — Controlled Execution Evidence / Mutation Receipt
- E7.76 — Collaboration Execution Authorization & External Action Boundary
- E7.77 — External Collaboration Execution Evidence & Result Reconciliation

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.78-r1
