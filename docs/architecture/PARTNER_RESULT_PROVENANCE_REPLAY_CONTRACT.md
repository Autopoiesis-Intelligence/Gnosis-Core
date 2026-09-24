# E8.18 — Partner Result Provenance Replay

## Objective
Prevent a returned partner result from entering self-learning when it cannot be proven to originate from the exact delivered core, transfer manifest and contract.

## Replay checks
Exact core digest, delivery ID, manifest ID and contract ID must match the expected delivery record. Evidence references are mandatory.

## Invariants
Any mismatch produces `REPLAY_REJECTED` and cannot enter learning. A verified replay only establishes provenance; it does not itself commit durable learning or grant execution authority.

## Status
PARTIAL / UNVERIFIED.
