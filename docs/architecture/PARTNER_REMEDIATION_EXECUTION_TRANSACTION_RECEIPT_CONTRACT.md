# E7.94 — Remediation Execution Transaction & Mutation Receipt Contract

## Objective

Define the governed execution boundary after E7.93 admission.

Execution MUST be an explicitly bounded operation that produces durable mutation evidence. A successful admission MUST NOT be treated as execution, and an execution result MUST NOT be treated as verification of the intended outcome.

## Preconditions

Execution MUST reference:

- exact accepted plan revision;
- exact authorization identity/revision;
- exact preflight/admission identity;
- target/resource identity;
- exact operation and parameters;
- execution actor;
- execution transaction identity;
- applicable execution policy revision.

## Execution states

An execution transaction MUST use explicit states:

- REQUESTED;
- STARTING;
- EXECUTING;
- COMMITTED;
- FAILED;
- ABORTED;
- ROLLED_BACK;
- UNKNOWN;
- SUPERSEDED.

COMMITTED means the governed mutation transaction committed. It does not prove that the intended business/result condition was achieved.

## Transaction boundary

Where the target system supports atomic transactions, the governed mutation MUST use the strongest available atomic boundary.

Where atomicity is unavailable, the system MUST explicitly record:

- mutation steps;
- completed steps;
- failed step;
- remaining steps;
- compensation/rollback status;
- resulting uncertainty.

The system MUST NOT claim atomicity when it was not available.

## Mutation receipt

Every execution attempt MUST produce a mutation receipt containing:

1. execution identity;
2. plan identity/revision;
3. authorization identity/revision;
4. admission identity;
5. target/resource identity;
6. exact operation/parameters;
7. actor identity;
8. pre-execution state identity where available;
9. transaction state;
10. mutation result;
11. post-execution state identity where available;
12. error/failure information;
13. ordering/timestamp evidence;
14. policy revision;
15. receipt digest/integrity identity.

The receipt MUST be append-only.

## Idempotency

Where an operation can be safely repeated, execution MUST use a stable idempotency identity.

A repeated request with identical execution identity MUST NOT create an unintended duplicate mutation.

If idempotency cannot be guaranteed, the system MUST fail closed or require explicit governed retry handling.

## Failure handling

FAILED means the transaction did not commit as declared.

UNKNOWN means the system cannot establish whether the mutation committed.

UNKNOWN MUST NOT be normalized to FAILED or COMMITTED without new evidence.

ABORTED means execution was intentionally stopped before the governed mutation completed.

ROLLLED_BACK/ROLLED_BACK means compensating action was recorded, not that the original execution never happened.

## Partial execution

If execution is non-atomic and partially completes:

- preserve every completed mutation step;
- preserve the failure point;
- preserve resulting resource state where observable;
- create explicit reconciliation requirements;
- do not represent the operation as fully successful.

## Retry

Retry MUST be a new governed execution attempt or an explicitly idempotent continuation.

A retry MUST reference the prior execution receipt.

Conflicting retry conditions MUST fail closed.

## Concurrency and stale admission

If target/resource state changes after preflight:

- execution MUST revalidate where required by policy;
- or fail closed;
- or use an explicitly authorized compare-and-swap/transaction condition.

Execution MUST NOT silently proceed against an incompatible state.

## Authorization consumption

For single-use or bounded-use authorization:

- successful consumption MUST be recorded;
- failed/unknown consumption MUST remain distinguishable;
- reuse outside declared limits MUST be blocked.

## Security and privacy

Execution MUST use minimum necessary data.

Secrets MUST NOT be copied into mutation receipts.

Receipts MUST contain references/identifiers instead of sensitive payloads where sufficient.

## Recovery and durability

Execution receipts and transaction states MUST survive restart/recovery.

Recovery MUST NOT fabricate COMMITTED state.

If commit status is uncertain after recovery, state MUST remain UNKNOWN until independently resolved.

## Authority separation

Preflight != execution
Execution != verification
Execution result != business outcome
Receipt != source payload
Rollback != history deletion
Execution != new authority

## Acceptance gate

E7.94 is satisfied only when implementation and tests demonstrate:

1. exact admission-to-execution binding;
2. explicit transaction state machine;
3. strongest available atomic boundary;
4. durable mutation receipt;
5. idempotency/duplicate protection;
6. failure/unknown distinction;
7. partial-execution handling;
8. retry provenance;
9. stale-state protection;
10. authorization consumption;
11. recovery durability;
12. privacy/security controls;
13. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.93 — Remediation Execution Admission & Preflight Gate
- E7.92 — Remediation Plan Authorization Boundary
- E7.81 — Remediation Execution Authorization & Controlled Compensation Execution
- E7.82 — Remediation Result Verification & Governed Closure

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.94-r1
