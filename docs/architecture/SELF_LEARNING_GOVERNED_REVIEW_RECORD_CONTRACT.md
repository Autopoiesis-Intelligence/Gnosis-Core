# E7.46 — Governed Proposal Review / Acceptance Record

## Objective

Create an immutable, provenance-preserving governance review record for a validated Self-Learning proposal.

## Boundary

This module records a governance decision; it does not make the decision.

Allowed decisions:
- ACCEPTED
- REJECTED
- DEFERRED

A review record MUST NOT itself mutate:
- contract artifacts;
- Ψ-Core state;
- permissions;
- partner access;
- runtime configuration.

Acceptance is a governance record and MUST NOT be interpreted as automatic execution.

## Preconditions

Only a proposal with a valid E7.45 validation result may enter review.

Proposal and validation identities MUST match.

Reviewer and reason MUST be explicit.

## Provenance

Each record contains:
- review_id;
- proposal_id;
- decision;
- reviewer;
- reason;
- validation digest;
- creation timestamp;
- provenance;
- authority classification.

For fixed inputs, review_id MUST be deterministic.

## Privacy

The review record contains contract/proposal metadata only and MUST NOT copy private user or partner payloads.

## Status

IMPLEMENTED / UNVERIFIED.

Implementation:
- gnosis/self_learning/governance.py
- tests/test_self_learning_governance.py
