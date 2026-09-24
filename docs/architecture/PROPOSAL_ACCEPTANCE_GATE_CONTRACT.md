# E8.04 — Proposal Review & Acceptance Gate

## Objective
Separate an automatically generated proposal from an accepted contract. Activation requires an explicit decision bound to the exact proposal digest.

## Decisions
ACCEPT, REJECT, REQUEST_CHANGES.

## Invariants
A decision must identify the actor/reference, reason, proposal ID and exact proposal digest. Only ACCEPT on a currently PROPOSED artifact may activate it. Review does not itself grant execution authority.

## Status
PARTIAL / UNVERIFIED.
