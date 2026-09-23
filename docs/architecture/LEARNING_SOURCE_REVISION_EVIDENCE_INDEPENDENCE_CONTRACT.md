# E7.12 — Learning Source Revision and Evidence Independence Contract

## Purpose

Prevent self-learning from treating stale, duplicated, copied, or common-origin material as independent evidence.

## Source revision binding

Every external learning source MUST be represented by:

- source_id;
- repository or origin;
- immutable revision identifier;
- acquisition/reference timestamp;
- declared scope;
- provenance;
- audit status;
- revocation/supersession status.

A learning item MUST retain the source revision from which it was derived.

## Independence relation

For evidence items e1 and e2, apparent independence is insufficient.

Define:

I(e1,e2) = 1 only when their relevant provenance paths do not share a known common source, transformation, dataset, model output, copied artifact, or other declared dependency.

If independence cannot be established:

I(e1,e2) = UNKNOWN

UNKNOWN MUST NOT be promoted to independent evidence.

## Evidence aggregation

Let E be a set of evidence items. Aggregation MUST preserve provenance groups:

E = ⋃ G_i

where each G_i represents evidence with a known common origin/dependency class.

Multiple observations from one provenance group MUST NOT be counted as equivalent to multiple independent confirmations.

## Learning boundary

Source evidence may:

Observation -> Finding -> Counterexample -> Candidate -> ShadowEvaluation

but:

ExternalEvidence -> CanonicalState

is forbidden.

## Revision invalidation

When a source revision is superseded or revoked, derived learning items MUST be marked for re-evaluation according to their dependency lineage.

Historical evidence remains retained and labeled; it is not silently deleted.

## Acceptance

The contract is accepted only when provenance groups, unknown independence, source revision invalidation, copied/common-origin evidence, and derived-item re-evaluation are represented and tested deterministically.

Status: DESIGNED / NOT_IMPLEMENTED.
