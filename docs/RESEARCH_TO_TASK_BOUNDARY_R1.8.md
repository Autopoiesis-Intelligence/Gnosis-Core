# Gnozis-V2 — Research Machine → Engineering Task Boundary R1.8

Status: CONTRACT / ACTIVE
Scope: provenance-to-task handoff; no automatic task creation or Core authority

## Purpose

Define the boundary between a Research Machine record and an engineering Task.

A Research Machine record may inform or motivate a Task, but it is not itself an engineering requirement, acceptance criterion, authorization, or proof.

## Canonical flow

```
Research Record
  ↓ research_ref
Task objective / scope / constraints
  ↓
acceptance criteria + evidence requirements
  ↓
Proposal / implementation
  ↓
Core verification and acceptance
```

## Required transformation rule

Research content MUST NOT be copied wholesale into Task canonical state.

The Task records only the engineering interpretation necessary to make the work bounded and testable:

- objective;
- allowed/forbidden scope;
- acceptance criteria;
- required evidence;
- relevant capabilities;
- baseline/context;
- non-authoritative research_refs.

## Relation semantics

A research reference relation may be:

- INFORMED_BY
- DERIVED_REQUIREMENT
- TEST_RATIONALE
- COUNTEREXAMPLE_SOURCE
- AUDIT_REFERENCE

The relation explains provenance. It does not establish truth.

## Task acceptance independence

A Task is valid only when its own objective, scope and acceptance criteria are explicit.

The presence of a Research Machine reference MUST NOT by itself:

- create a Task;
- mark a Task valid;
- mark a requirement accepted;
- authorize execution;
- satisfy evidence requirements.

## Example

```yaml
objective: Verify that evidence generation cannot use post-transition information.
acceptance_criteria:
  - temporal-leakage test exists
  - test fails under injected leakage
  - test passes without leakage
evidence_required:
  - reproducible test result
research_refs:
  - repository: Mikhail-Kucheriavyi-23/Gnozis
    record_id: C-0004
    source_commit: 7eb7caeb6a82e09e3bf40feef515b4db25b3eb0c
    relation: TEST_RATIONALE
```

The example demonstrates provenance linkage; the research record remains non-authoritative.

## Implementation boundary

R1.8 defines a contract only. It does not implement automatic research-to-task generation, connectors, agents, or Core changes.

Any future generator must be separately scoped, auditable, and subject to the existing Task lifecycle and Core ingress contracts.

## Acceptance

R1.8 is complete when an engineering Task can retain reproducible Research Machine provenance while independently expressing its objective, scope, acceptance criteria, and evidence requirements without importing research authority.
