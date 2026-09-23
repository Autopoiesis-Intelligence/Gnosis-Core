# E7.50 — Self-Learning Evidence Replay / Reconstruction

## Objective

Reconstruct and validate a complete Self-Learning evidence sequence from the append-only ledger.

## Boundary

Replay is evidence reconstruction only. It MUST NOT:
- execute a proposal;
- authorize a change;
- mutate contracts or Core;
- infer missing events;
- repair damaged history.

## Requirements

Replay MUST:
- preserve ledger order;
- verify hash-chain integrity;
- detect subject mixing when a flow identifier is supplied;
- report missing/broken genesis linkage;
- return explicit errors rather than silently repairing history.

A valid replay proves structural continuity of the recorded evidence chain, not truth of the underlying events.

## Status

IMPLEMENTED / UNVERIFIED.
