# E7.114 — First Actual Proof Run Scope Lock & Target Commit Record Contract

## Objective

Create the concrete, auditable scope-lock record for the first actual Self-Learning proof run defined by E7.113.

E7.114 MUST identify exactly what will be executed before execution begins.

## Scope-lock record

The record MUST contain:

- batch ID;
- scope-lock ID;
- repository;
- branch/ref;
- exact target commit SHA;
- selected contract IDs;
- selected criterion IDs;
- implementation paths;
- test/runtime paths;
- expected outcomes;
- evidence capture destinations/references;
- environment prerequisites;
- stop conditions;
- active evidence policy revision;
- active verification-matrix revision;
- active progress-calculation policy revision.

## Selection integrity

The scope MUST be derived from the frozen E7.106 selection.

No candidate may be silently added, removed or substituted.

Any change MUST:

1. invalidate the current scope lock;
2. create a new scope-lock revision;
3. preserve the previous record;
4. re-establish readiness under E7.107.

## Exact-commit lock

The target SHA MUST resolve unambiguously.

The scope lock MUST fail if:

- the ref resolves to another commit;
- required files differ from the locked revision;
- test/runtime paths are unavailable at the target commit;
- evidence cannot be bound to the target SHA.

## Minimal proof scope

The first run SHOULD use the smallest deterministic scope that can produce meaningful criterion-level evidence.

Scope minimization MUST NOT remove mandatory trust-boundary or failure-path checks required by the selected criteria.

## Pre-execution validation

Before execution, validate:

- repository access;
- target commit;
- selected files;
- test commands;
- environment;
- evidence capture;
- policy revisions;
- stop conditions.

Each validation MUST have an explicit result.

## Scope freeze

After successful lock:

- scope is immutable;
- target commit is immutable;
- criteria are immutable;
- commands are immutable;
- progress MUST remain unchanged.

Execution may proceed only against the locked record.

## Failure and invalidation

If any locked prerequisite becomes invalid:

- mark scope lock INVALIDATED;
- prevent execution;
- preserve the record;
- create a new revision after correction.

Invalidated scope locks MUST NOT produce verification credit.

## Auditability

The scope-lock record MUST be sufficient for an independent reviewer to determine exactly what was intended to run before seeing execution results.

## Acceptance gate

E7.114 is satisfied only when implementation and tests demonstrate:

1. concrete batch scope;
2. exact target commit;
3. criterion/path mapping;
4. pre-execution validation;
5. immutable scope lock;
6. invalidation/revision behavior;
7. no progress change from scope locking;
8. independent auditability;
9. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.113 — First Verification Batch Actual Proof Run
- E7.106 — First Verification Batch Candidate Inventory & Selection Record
- E7.107 — First Verification Batch Execution Readiness Gate

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.114-r1
