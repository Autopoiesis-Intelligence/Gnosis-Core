# E8.0 — First Governed Task Acceptance Contract

## Objective

Define the smallest real end-to-end task that can demonstrate a governed learning loop without requiring self-modification of production code.

## Required stages

User input → Candidate → Test → Select → Verify → Governance → Commit → Evidence → Replay → Audit.

## Scope

The task MUST operate inside an explicitly declared, isolated mutation scope. The first task MUST NOT modify production code, authorization rules, or trust-boundary enforcement.

## Required identities

The execution record MUST bind, at minimum:

- input identity
- initial state identity and digest
- candidate identity
- selected result identity
- authorization/scope identity
- commit identity
- evidence/provenance identity

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

## First-task constraint

The first task should be intentionally small and deterministic enough that a human can independently inspect the complete evidence chain.

## Evidence levels

DESIGN → IMPLEMENTED → REACHABLE → RUNTIME → PERSISTED → AUDITED → CI_PROVEN.

The E8.0 contract is not considered closed until the complete task reaches RUNTIME and the resulting evidence is persisted and auditable.

## Status

CONTRACT DEFINED / IMPLEMENTATION NOT STARTED.
