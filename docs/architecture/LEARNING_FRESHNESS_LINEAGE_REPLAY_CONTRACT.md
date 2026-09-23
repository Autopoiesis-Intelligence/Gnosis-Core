# E7.11 — Learning Freshness, Lineage and Replay Contract

## Purpose
Prevent stale, duplicated or replayed learning evidence from silently influencing current self-learning decisions.

## Required binding
Every learning-derived Finding, Counterexample, Candidate and RuleProposal MUST bind to source_id, source_revision or immutable commit, evidence identifiers, relevant Core state/parent hash where applicable, contract revision, creation timestamp/epoch, and provenance lineage.

## Freshness rule
Historical existence of evidence does not imply current validity. An item becomes stale when its validity scope is exceeded or a superseding source/state revision invalidates its assumptions.

## Replay rule
Re-submitting the same learning event MUST NOT create a new epistemic fact merely by changing transport/session identity. Cross-revision replay, cross-scope replay and superseded-proposal replay MUST be rejected or explicitly classified as historical evidence.

## Lineage
Derived items preserve parent evidence and transformation lineage. Lineage is append-only; supersession creates a new revision rather than rewriting the previous item.

## Learning safety invariant
ValidNow(item, context) != Exists(item)

Replay(item, new_session) does not imply NewEvidence.

## Acceptance
Acceptance requires deterministic freshness/replay decisions, persisted lineage, explicit supersession, and tests for same-event reuse, cross-revision replay, stale source, parent-state mismatch and revoked source.

Status: DESIGNED / PARTIALLY COVERED BY EXISTING AUTHORITY/PROPOSAL LINEAGE; learning-specific end-to-end verification NOT_IMPLEMENTED.
