# E8.0 — First Governed Task Acceptance Contract

## Objective

Define the smallest real end-to-end task that can demonstrate a governed learning loop without requiring self-modification of production code.

## Required stages

User input → Candidate → Test → Select → Verify → Governance → Commit → Evidence → Replay → Audit.

## First task

The first task SHALL be a deterministic transformation of one isolated learning record.

Initial fixture:

- record_id: `E80-FIRST-TASK-001`
- version: 1
- value: A

Requested transformation:

- value A → B
- increment version by exactly 1

The expected final state is therefore:

- record_id: `E80-FIRST-TASK-001`
- version: 2
- value: B

The task is intentionally small so that every transition and every persisted artifact can be independently inspected.

## Mutation scope

The mutation scope is limited to the isolated first-task learning record and its dedicated evidence artifacts.

The first task MUST NOT modify:

- production source code;
- authorization rules;
- governance policy;
- workflow definitions;
- trust-boundary enforcement;
- unrelated repository state.

Any attempt to mutate outside this scope MUST fail closed and MUST NOT produce the governed commit.

## Required stages

User input → Candidate → Test → Select → Verify → Governance → Commit → Evidence → Replay → Audit.

## Required identities

The execution record MUST bind, at minimum:

- input identity;
- initial state identity and digest;
- candidate identity;
- selected result identity;
- authorization/scope identity;
- commit identity;
- evidence/provenance identity.

## Success criteria

A run is successful only when all required stages are reached and the resulting evidence permits reconstruction of the execution without relying on hidden mutable state.

RESULT alone is insufficient.

Success = RESULT + AUTHORITY + TRACEABILITY + REPLAY + AUDIT.

## Fail-closed criteria

The task MUST be rejected when:

- authorization is absent or invalid;
- the requested mutation is outside the declared scope;
- state identity is substituted;
- content identity is substituted;
- required evidence cannot be persisted;
- replay cannot reconstruct the committed result.

A rejected execution MUST NOT produce the governed commit.

## Evidence levels

DESIGN → IMPLEMENTED → REACHABLE → RUNTIME → PERSISTED → AUDITED → CI_PROVEN.

The E8.0 contract is not considered closed until the complete task reaches RUNTIME and the resulting evidence is persisted and auditable.

## Status

CONTRACT DEFINED / FIRST TASK SPECIFIED / IMPLEMENTATION NOT STARTED.
