# E7.109 — First Verification Batch Evidence Acceptance & Criterion Promotion Gate Contract

## Objective

Define the controlled decision boundary that converts captured execution evidence from E7.108 into ACCEPTED evidence and, where all requirements are met, promotes individual criteria through IMPLEMENTED/VERIFIED states.

E7.109 MUST NOT allow execution records to self-promote into verification.

## Acceptance pipeline

The decision flow MUST be:

EXECUTION EVIDENCE → PROVENANCE VALIDATION → CRITERION CHECK → ACCEPTED / REJECTED / CONFLICT → CRITERION PROMOTION

Only ACCEPTED evidence may support criterion promotion.

## Provenance validation

For each evidence item verify:

- batch identity;
- execution attempt identity;
- exact target commit;
- contract/revision;
- criterion ID;
- test/command identity;
- environment identity;
- expected result;
- observed result;
- artifact/reference integrity;
- evidence policy revision.

Missing or contradictory provenance MUST prevent acceptance.

## Criterion promotion rules

A criterion may become IMPLEMENTED only when:

1. required implementation exists at target commit;
2. mapped execution evidence demonstrates the implementation behavior;
3. evidence is ACCEPTED;
4. all implementation-level dependencies are satisfied.

A criterion may become VERIFIED only when:

1. all mandatory verification evidence is ACCEPTED;
2. expected behavior is demonstrated;
3. required failure/recovery/integrity scenarios are satisfied where applicable;
4. no unresolved conflict invalidates the evidence;
5. exact-commit binding remains valid.

## Partial results

If evidence proves only part of a criterion:

- retain accepted partial evidence;
- mark criterion PARTIAL;
- identify missing proof;
- do not grant VERIFIED credit.

A failed or absent test MUST NOT be converted into successful evidence by interpretation.

## Conflict handling

Conflicting evidence MUST produce CONFLICT.

CONFLICT MUST:

- block promotion for the affected criterion;
- preserve all conflicting evidence;
- identify the conflict;
- require explicit resolution under governance policy.

## Metric boundary

Criterion promotion may affect:

- Implementation %;
- Verification %;
- Runtime Proof %;
- Self-Learning Overall %.

The exact delta MUST be calculated by the active versioned progress policy.

No promotion may occur without an auditable accepted evidence reference.

## Batch-level result

The batch MUST produce a criterion-level result set:

- VERIFIED;
- IMPLEMENTED;
- PARTIAL;
- BLOCKED;
- FAILED;
- CONFLICT.

Batch success MUST NOT imply that every selected criterion is VERIFIED.

## Regression protection

Promotion MUST be append-only.

If later evidence invalidates a previously verified criterion:

- preserve the original promotion;
- create a new evidence/criterion state;
- require re-verification;
- do not rewrite historical evidence.

## Recovery and replay

Acceptance/promotion state MUST survive restart.

Identical acceptance requests MUST be idempotent.

Conflicting duplicate acceptance requests MUST fail closed.

Recovery MUST NOT fabricate ACCEPTED or VERIFIED states.

## Authority separation

Execution record != evidence acceptance
Evidence acceptance != criterion verification
Criterion verification != progress calculation
Progress calculation != Ψ-Core mutation

## Acceptance gate

E7.109 is satisfied only when implementation and tests demonstrate:

1. provenance validation;
2. criterion-specific acceptance;
3. deterministic promotion;
4. partial-result handling;
5. conflict blocking;
6. metric integration;
7. append-only promotion history;
8. regression protection;
9. duplicate/replay safety;
10. recovery integrity;
11. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.108 — First Verification Batch Execution Record & Evidence Capture
- E7.103 — Self-Learning Evidence-to-Contract Verification Matrix
- E7.102 — Self-Learning Evidence Ingestion & Acceptance Pipeline
- E7.101 — Self-Learning Evidence Registry & Reproducible Progress Ledger

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.109-r1
