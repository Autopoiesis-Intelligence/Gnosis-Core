# E7.78 — External Collaboration Failure / Compensation / Recovery Boundary

## Objective
Prevent failed external collaboration actions from silently entering Self-Learning as successful outcomes.

## Recovery states
NO_ACTION, COMPENSATION_REQUIRED, COMPENSATED, MANUAL_REVIEW, COMPENSATION_FAILED, NOT_COMPENSATABLE.

## Invariants
Original execution evidence is immutable by reference. Compensation requires its own contract and provenance. MANUAL_REVIEW and failed/unknown recovery are not learning-eligible.

## Boundary
Recovery does not rewrite the original execution evidence and does not grant new authority. Any external compensation action requires a separately authorized execution path.

## Status
PARTIAL / UNVERIFIED.
