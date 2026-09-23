# E7.102 — Self-Learning Evidence Ingestion & Acceptance Pipeline Contract

## Objective

Define the controlled pipeline by which implementation, runtime, CI and audit evidence enters the E7.101 ledger and becomes eligible for progress calculation.

Evidence ingestion MUST be provenance-bound and MUST NOT permit manual status promotion to VERIFIED.

## Pipeline

Evidence MUST pass:

SUBMITTED → RECORDED → VALIDATED → ACCEPTED / REJECTED / CONFLICT

Only ACCEPTED evidence may contribute to progress metrics.

Acceptance MUST be contract- and criterion-specific.

## Submission requirements

Each submission MUST identify:

- contract/task ID;
- contract revision;
- evidence type;
- repository;
- ref/branch;
- exact commit SHA;
- source identity;
- test/CI/runtime invocation;
- observed result;
- expected result;
- relevant acceptance criterion;
- evidence payload or immutable reference;
- submission identity;
- submission metadata.

Missing mandatory provenance MUST prevent acceptance.

## Source classes

Evidence sources MUST be classified:

- CI;
- runtime;
- integration test;
- unit/property test;
- failure injection;
- recovery/replay test;
- external audit;
- static inspection;
- documentation.

The source class MUST NOT override acceptance requirements.

## Validation

Validation MUST check:

1. exact commit;
2. contract revision;
3. evidence source identity;
4. test/run identity where applicable;
5. expected versus observed result;
6. acceptance criterion mapping;
7. dependency state;
8. duplicate identity;
9. integrity metadata;
10. policy compatibility.

Invalid or unverifiable evidence MUST be rejected or marked CONFLICT.

## Acceptance authority

Acceptance MUST be deterministic under the active evidence policy.

No free-form status edit may create ACCEPTED evidence.

Where human/governance review is required, the review itself MUST become evidence with:

- reviewer identity;
- policy revision;
- decision;
- rationale;
- referenced evidence.

## Duplicate and replay handling

Identical evidence submission MUST be idempotent.

Conflicting submissions sharing an evidence identity MUST fail closed and enter CONFLICT.

A later commit MUST create a new evidence record rather than mutate an earlier record.

## Acceptance-to-progress boundary

ACCEPTED evidence contributes only to the metric(s) explicitly supported by its mapped acceptance criteria.

For example:

- documentation may support coverage/specification evidence;
- successful runtime/CI evidence may support implementation/verification;
- recovery evidence supports only criteria requiring recovery behavior.

Evidence MUST NOT receive broader credit than its acceptance mapping permits.

## Failure handling

If ingestion fails after evidence receipt:

- preserve the receipt if durable;
- identify ingestion state;
- permit deterministic retry;
- prevent partial acceptance from being represented as complete acceptance.

## Security and privacy

Evidence ingestion MUST apply minimum necessary data.

Secrets, credentials and unrelated sensitive payloads MUST NOT enter the progress ledger.

References/digests SHOULD be preferred over copying raw sensitive artifacts.

## Recovery

Ingestion state MUST survive restart/recovery.

Recovery MUST NOT duplicate accepted evidence or fabricate validation/acceptance.

Interrupted ingestion MUST resume or fail deterministically.

## Auditability

Every acceptance/rejection/conflict decision MUST be reconstructable from:

submission → validation → policy → decision → ledger record.

Historical decisions MUST remain immutable.

## Authority separation

Evidence ingestion != contract implementation
Evidence acceptance != verification of system behavior
Evidence acceptance != Ψ-Core mutation
Progress calculation != evidence creation

## Acceptance gate

E7.102 is satisfied only when implementation and tests demonstrate:

1. controlled submission pipeline;
2. exact-commit validation;
3. criterion-level mapping;
4. deterministic acceptance;
5. human-review evidence where required;
6. duplicate/replay handling;
7. bounded metric credit;
8. failure/retry behavior;
9. privacy/security controls;
10. recovery integrity;
11. reconstructable acceptance audit;
12. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.101 — Self-Learning Evidence Registry & Reproducible Progress Ledger
- E7.100 — Self-Learning Contract Completion & Evidence Gate
- Existing persistence/audit-chain architecture

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.102-r1
