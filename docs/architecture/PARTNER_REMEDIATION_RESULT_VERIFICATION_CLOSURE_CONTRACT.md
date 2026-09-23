# E7.82 — Remediation Result Verification & Governed Closure Contract

## Objective

Define the verification boundary after a remediation or compensation execution.

E7.82 determines whether the observed post-execution state is sufficiently evidenced to verify the remediation objective and whether the related incident may be closed.

Verification and closure do not authorize new execution, rewrite evidence, mutate Ψ-Core or broaden authority.

## Verification inputs

Verification MUST reference:

- exact incident and resolution;
- exact remediation plan revision;
- exact execution authorization;
- exact execution attempt/evidence;
- intended remediation objective;
- target resource;
- authorized scope;
- observed post-execution state;
- privacy classification;
- required verification criteria.

## Verification states

A verification MUST use an explicit state:

- NOT_VERIFIED;
- VERIFIED;
- FAILED;
- PARTIAL;
- UNKNOWN;
- SUPERSEDED;
- REJECTED.

VERIFIED means the defined objective is supported by sufficient evidence. It does not mean that the system is permanently correct.

## Closure states

Incident closure MUST use an explicit state:

- OPEN;
- READY_FOR_CLOSURE;
- CLOSED;
- REOPENED;
- BLOCKED.

CLOSED is permitted only when the closure criteria are satisfied.

## Verification record

The record MUST bind:

1. exact incident/resolution identity;
2. exact plan revision;
3. exact authorization;
4. exact execution evidence;
5. expected target state;
6. observed target state;
7. verification method/evidence;
8. verification result;
9. unresolved limitations;
10. closure decision;
11. verifier identity;
12. revision/provenance;
13. verification digest.

## Verification rules

Verification MUST compare the observed result with the declared remediation objective.

A successful execution result alone is insufficient when the objective requires independent state verification.

Where an external target provides a verifiable revision/digest/state, the verifier SHOULD use it.

If required evidence is unavailable, verification MUST be UNKNOWN or NOT_VERIFIED rather than inferred.

## Partial and unknown results

PARTIAL means that only part of the objective is evidenced.

UNKNOWN means that available evidence cannot establish the target state.

Neither state permits normal CLOSED status unless a separate governance rule explicitly permits closure with documented residual risk.

Residual uncertainty MUST remain visible.

## Reopen rules

An incident MUST be REOPENED when:

- later evidence contradicts the verification;
- the target state diverges from the verified state;
- a hidden scope violation is discovered;
- required evidence is invalidated;
- the remediation objective is shown to be incomplete.

Reopening MUST preserve the prior closure record.

## Closure rules

CLOSED requires:

- verified remediation objective;
- complete provenance;
- no unresolved blocking conflict;
- explicit closure decision;
- recorded limitations where applicable.

Closure does not erase incident history.

A closed incident remains queryable as historical evidence.

## Fail-closed behavior

Verification MUST fail closed when:

- provenance links are inconsistent;
- execution identity is ambiguous;
- observed target differs unexpectedly;
- privacy classification is missing/conflicting;
- verification evidence is insufficient;
- conflicting replay is detected.

## Authority separation

Verification != Execution
Verification != Authorization
Closure != Authority
Closure != History deletion
Verified result != Core mutation

No verification or closure record may grant new external permissions or modify Ψ-Core.

## Recovery and replay

Verification and closure state MUST survive restart/recovery.

Conflicting verification replay MUST fail closed.

A superseding verification MUST preserve linkage to the previous verification.

Historical closure decisions MUST remain reconstructable.

## Acceptance gate

E7.82 is satisfied only when implementation and tests demonstrate:

1. exact execution-to-verification provenance;
2. explicit verification state machine;
3. objective/state comparison;
4. correct PARTIAL/UNKNOWN handling;
5. closure gating;
6. reopen on contradictory evidence;
7. preservation of historical closure;
8. conflicting replay rejection;
9. restart/recovery integrity;
10. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.77 — External Collaboration Execution Evidence & Result Reconciliation
- E7.79 — Governed External Collaboration Incident & Conflict Resolution
- E7.80 — Governed Remediation Plan & Compensation Authorization
- E7.81 — Remediation Execution Authorization & Controlled Compensation Execution

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.82-r1
