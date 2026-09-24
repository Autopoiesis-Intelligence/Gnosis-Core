# E8.01 — Dynamic Opportunity Reclassification

## Objective
Allow opportunity value to change as evidence accumulates, while preserving the previous classification and requiring explicit evidence for every transition.

## Transition
LOW_RELEVANCE → RESEARCH_RELEVANT → COMMERCIAL is permitted only as an evidence-backed proposal; reverse transitions are also allowed when later evidence changes the classification.

## Invariants
Every reclassification records previous level, proposed level, evidence, reason and status. Same-level changes are no-ops. Reclassification does not itself create execution authority or a commercial contract.

## Status
PARTIAL / UNVERIFIED.
