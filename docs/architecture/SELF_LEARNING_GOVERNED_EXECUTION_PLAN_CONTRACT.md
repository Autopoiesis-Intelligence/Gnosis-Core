# E7.47 — Governed Execution / Controlled Contract Application Plan

## Objective

Create an explicit execution plan from an ACCEPTED governance record while preserving a hard separation between governance and mutation.

## Boundary

This contract creates a plan only.

It MUST NOT:
- mutate contract artifacts;
- mutate Ψ-Core;
- change permissions;
- change partner access;
- execute shell commands;
- perform network side effects;
- silently select an execution target.

## Preconditions

Only a governance record with:
- authority = governance-record-only;
- decision = ACCEPTED;
- matching proposal identity;
- validation evidence

may produce an execution plan.

The plan MUST declare:
- execution target requirement;
- external execution authority requirement;
- governance/proposal identity;
- deterministic plan ID.

## Execution rule

The plan action is declarative:

APPLY_GOVERNED_PROPOSAL_AFTER_EXTERNAL_AUTHORIZATION

An external, explicitly authorized execution layer remains responsible for any mutation.

## Status

IMPLEMENTED / UNVERIFIED.

Implementation:
- gnosis/self_learning/execution.py
- tests/test_self_learning_execution.py
