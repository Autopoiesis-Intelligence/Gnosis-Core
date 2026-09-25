# R3.1 — Autonomous Cycle Evidence Loop

## Objective

Record one autonomous learning/evolution cycle as an immutable, provenance-bound evidence object.

## Causal chain

Input → Candidate → Execution → Verification → Commit/Reject → Learning → Next Cycle.

CycleEvidence carries the identity required to reconstruct that chain without granting execution authority.

## Invariants

- cycle_id is mandatory.
- initial_state_digest is mandatory.
- candidate, execution and verification identities are mandatory.
- accepted outcomes require a commit identity.
- rejected/inconclusive outcomes cannot carry a commit identity.
- evidence references are mandatory and deterministically ordered.
- the evidence digest is derived from the complete canonical record.
- evidence never grants execution authority.
- identical initial/result state digests are detectable as a no-op.
- a learning identity is required before evidence can be considered to influence a later cycle.

## Scope

This is an evidence boundary, not an autonomous mutation engine. It does not execute candidates, select candidates, mutate Core, or authorize commits.

## Acceptance

The acceptance test must demonstrate:

1. deterministic evidence identity;
2. exact cycle/state causal binding;
3. accepted commit requirement;
4. rejected commit prohibition;
5. learning influence only with a learning identity;
6. no-op detection;
7. evidence requirement;
8. no execution authority.

Runtime/CI evidence is required before this contract is marked VERIFIED.
