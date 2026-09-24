# E7.87 — External Audit Challenge, Dispute & Evidence Reconciliation

## Objective
Provide a durable challenge path for audit claims without silently mutating the attested package or deleting disputed evidence.

## Invariants
A challenge binds to the attestation, package and challenged digest. Resolution requires explicit resolution evidence and matching package digest. Challenge history remains durable. A challenge does not itself revoke or grant execution authority.

## Status
PARTIAL / UNVERIFIED.
