# E7.101 — Self-Learning Evidence Registry & Reproducible Progress Ledger Contract

## Objective

Define the durable evidence registry required to calculate Self-Learning progress reproducibly under E7.100.

The ledger MUST make every progress transition traceable to an exact contract revision, implementation evidence, verification evidence and calculation-policy revision.

## Required record

Each progress evidence record MUST contain:

- contract/task identifier;
- contract revision;
- repository and ref;
- exact commit SHA;
- evidence type;
- implementation/test paths;
- test command or CI run identity;
- observed result;
- evidence status;
- timestamp/order evidence where available;
- dependency state;
- calculation-policy revision;
- record integrity identifier.

## Evidence types

At minimum:

- SPECIFICATION;
- IMPLEMENTATION;
- UNIT_TEST;
- INTEGRATION_TEST;
- FAILURE_INJECTION;
- RECOVERY_TEST;
- REPLAY_TEST;
- CI_RUN;
- EXTERNAL_AUDIT;
- RUNTIME_OBSERVATION.

Evidence type MUST NOT by itself establish VERIFIED status; acceptance criteria determine sufficiency.

## Progress ledger states

A ledger entry MUST use:

- RECORDED;
- ACCEPTED;
- REJECTED;
- SUPERSEDED;
- CONFLICT;
- INTEGRITY_FAILURE.

Rejected or superseded evidence MUST remain historically visible.

## Exact-commit rule

Evidence accepted for IMPLEMENTED/VERIFIED MUST resolve to the exact commit claimed.

A later commit MAY establish new evidence only through a new ledger entry.

Copied, ambiguous or unverifiable evidence MUST NOT count toward progress.

## Calculation

The ledger MUST support deterministic calculation of:

- Contract Coverage %;
- Implementation %;
- Verification %;
- Runtime Proof %;
- Self-Learning Overall %.

The formula, weights, denominator and exclusions MUST be versioned.

Adding a contract changes the denominator only according to the active calculation policy; it MUST NOT itself create completion credit.

## Conflict handling

If two evidence records conflict:

- preserve both;
- mark CONFLICT;
- identify the affected contract/metric;
- prevent the conflicting evidence from silently increasing progress;
- route resolution through governed review.

## Integrity

The ledger MUST provide tamper-evident identity/provenance for accepted progress evidence.

Historical accepted evidence MUST NOT be silently edited or deleted.

Corrections MUST append a new record.

## Recovery and replay

The ledger MUST survive restart/recovery.

Identical evidence submission MAY be idempotent when all identity and content fields match.

Conflicting duplicate submission MUST fail closed.

Recovery MUST NOT fabricate accepted evidence or progress.

## Acceptance gate

E7.101 is satisfied only when implementation and tests demonstrate:

1. durable evidence records;
2. exact-commit binding;
3. evidence-type classification;
4. deterministic metric calculation;
5. versioned calculation policy;
6. conflict handling;
7. tamper-evident history;
8. duplicate/replay protection;
9. recovery integrity;
10. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.100 — Self-Learning Contract Completion & Evidence Gate
- E7.99 — Post-Closure Evidence Integrity Verification & Provenance Checkpoint
- Existing audit/persistence architecture

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.101-r1
