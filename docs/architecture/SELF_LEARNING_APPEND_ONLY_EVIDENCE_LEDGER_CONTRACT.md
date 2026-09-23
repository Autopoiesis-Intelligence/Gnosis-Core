# E7.49 — Append-Only Self-Learning Evidence Ledger

## Objective
Provide a deterministic hash-linked evidence chain connecting Self-Learning artifacts without becoming an authority mechanism.

## Event model
Each event records:
- event_id;
- event_type;
- subject_id;
- payload_digest;
- previous_event_digest;
- event_digest;
- provenance;
- authority.

The chain begins at GENESIS.

## Integrity
For every event:
event_digest = SHA256(event_type, subject_id, payload_digest, previous_event_digest)

Any modification to an event or its ordering MUST be detectable by verify_chain.

## Boundary
The ledger:
- does not execute;
- does not authorize;
- does not mutate Core;
- does not mutate contracts;
- does not store private payloads;
- stores digests and metadata only.

## Append-only semantics
Existing events are evidence and MUST NOT be rewritten by the ledger API. New events extend the chain.

## Status
IMPLEMENTED / UNVERIFIED.
