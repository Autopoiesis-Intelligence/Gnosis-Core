# E8.05 — Contract Execution Boundary

## Objective
Separate contract acceptance from execution authorization and bind execution to the exact accepted contract digest, scope, task and expected result.

## Invariants
Execution authorization requires an accepted contract. Execution is permitted only when contract ID, exact digest and scope match the authorization. Authorization does not create or modify contracts.

## Status
PARTIAL / UNVERIFIED.
