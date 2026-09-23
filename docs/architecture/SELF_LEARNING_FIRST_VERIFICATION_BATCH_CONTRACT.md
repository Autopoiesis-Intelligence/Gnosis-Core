# E7.104 — First Self-Learning Verification Batch & Baseline Evidence Gate Contract

## Objective

Define the first bounded verification batch that converts the Self-Learning contract framework from design-only evidence toward reproducible IMPLEMENTED/VERIFIED evidence.

The batch MUST be conservative: no criterion receives credit beyond demonstrated evidence.

## Batch selection

The first batch MUST select contracts using:

1. direct dependency availability;
2. highest trust-boundary relevance;
3. deterministic testability;
4. existing implementation proximity;
5. minimal cross-family dependency;
6. ability to execute on an exact repository commit.

The selection rationale MUST be recorded.

## Baseline snapshot

Before execution, record:

- repository/ref;
- exact baseline commit;
- contract revisions;
- current metric values;
- current criterion states;
- known proof gaps;
- active evidence policy revision;
- test environment identifier where available.

The baseline MUST remain immutable.

## Batch scope

Each batch MUST define:

- selected contract IDs;
- selected criterion IDs;
- exact target commit;
- implementation paths;
- test paths/commands;
- required runtime scenarios;
- expected results;
- evidence records to be produced;
- stop/fail criteria.

Unselected contracts MUST NOT receive progress credit from the batch.

## Execution

The batch MUST execute the mapped proof paths from E7.103.

At minimum, applicable scenarios MUST include:

- normal success;
- invalid input/failure;
- duplicate/replay;
- restart/recovery;
- integrity/tamper;
- conflicting state where applicable.

The batch MUST use actual executable tests or runtime evidence.

## Result classification

Each criterion MUST resolve to one of:

- VERIFIED;
- IMPLEMENTED;
- PARTIAL;
- BLOCKED;
- FAILED.

FAILED MUST preserve the observed failure and evidence.

A batch MAY succeed while individual criteria remain unresolved.

## Evidence acceptance

Evidence MUST pass E7.102 before affecting progress.

Every accepted result MUST bind to the exact target commit.

Evidence from an unrelated or later commit MUST NOT be substituted.

## Baseline comparison

After execution, calculate deltas for:

- Contract Coverage %;
- Implementation %;
- Verification %;
- Runtime Proof %;
- Self-Learning Overall %.

The calculation MUST use the same policy revision as the baseline unless a new policy revision is explicitly introduced.

If a metric changes, the ledger MUST identify the exact accepted evidence responsible.

## Failure gate

The batch MUST fail closed for progress purposes if:

- exact commit cannot be established;
- required evidence is missing;
- acceptance mapping is ambiguous;
- evidence conflicts remain unresolved;
- tests did not actually execute;
- recovery/replay proof required by the selected criterion is absent.

A failed batch MUST NOT erase the baseline.

## No-gaming rule

The first batch MUST NOT be optimized to maximize percentage.

Selection is based on proof value and trust-boundary relevance, not metric gain.

Documentation-only completion MUST NOT count as verification.

## Recovery and audit

Batch state, baseline, execution results and evidence references MUST survive restart/recovery.

Re-running the identical batch MAY be idempotent only when commit, scope, policy and evidence identity are identical.

Conflicting reruns MUST create explicit conflict evidence.

## Acceptance gate

E7.104 is satisfied only when implementation and tests demonstrate:

1. reproducible baseline snapshot;
2. deterministic batch selection;
3. exact-commit execution;
4. actual mapped tests/runtime scenarios;
5. accepted evidence generation;
6. criterion-level result classification;
7. before/after metric calculation;
8. failure/stop behavior;
9. no-gaming selection;
10. recovery/audit continuity;
11. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.103 — Self-Learning Evidence-to-Contract Verification Matrix
- E7.102 — Self-Learning Evidence Ingestion & Acceptance Pipeline
- E7.101 — Self-Learning Evidence Registry & Reproducible Progress Ledger
- E7.100 — Self-Learning Contract Completion & Evidence Gate

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.104-r1
