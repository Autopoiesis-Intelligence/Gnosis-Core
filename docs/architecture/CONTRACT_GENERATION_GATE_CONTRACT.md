# E8.14 — Contract Generation Gate

## Objective
Generate a deterministic contract only from an accepted proposal and bind the contract to the exact proposal digest.

## Required content
Scope, rights profile, acceptance criteria, evidence requirements and transfer boundary.

## Invariants
Rejected/unaccepted proposals cannot generate contracts. Generated contracts remain bound to the exact proposal. DRAFT contracts are not executable; execution readiness is a separate state.

## Status
PARTIAL / UNVERIFIED.
