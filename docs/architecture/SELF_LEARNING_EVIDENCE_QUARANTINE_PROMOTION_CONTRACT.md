# E7.16 — Self-Learning Evidence Quarantine and Promotion Contract

## Objective

Define the explicit state machine between externally supplied learning material and material eligible for Core verification.

## States

UNSEEN -> RECEIVED -> IDENTITY_CHECKED -> PROVENANCE_CHECKED -> REVISION_CHECKED -> INDEPENDENCE_CLASSIFIED -> QUARANTINED -> EVALUATED -> VERIFIED -> GOVERNED -> PROMOTABLE

Terminal rejection states:

REJECTED, REVOKED, STALE, INVALID, CONFLICTED.

## Promotion invariant

Evidence in QUARANTINED or EVALUATED state MUST NOT mutate canonical state.

Only VERIFIED + GOVERNED material may become PROMOTABLE.

PROMOTABLE does not itself authorize execution; existing Commit/Authority boundaries remain mandatory.

## Conflict preservation

Conflicting evidence MUST remain separately addressable. Resolution must add a new evaluation/provenance record rather than overwrite either source.

## Re-evaluation

Changes to identity, source revision, parent state, independence classification, contract revision, or governance policy MUST invalidate promotion eligibility and trigger re-evaluation.

## Idempotency

Repeated ingestion of the same immutable evidence identity MUST be idempotent. A new transport/session identifier does not create a new evidence identity.

## Acceptance

Tests must cover every state transition, illegal promotion, duplicate ingestion, revocation, staleness, conflict preservation, policy change and re-evaluation.

Status: DESIGNED / NOT_IMPLEMENTED.
