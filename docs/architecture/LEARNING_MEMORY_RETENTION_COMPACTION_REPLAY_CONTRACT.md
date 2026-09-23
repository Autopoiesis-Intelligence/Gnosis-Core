# E7.20 — Learning Memory Retention, Compaction and Replay Contract

## Objective

Control growth of self-learning memory without destroying the evidence required to explain, audit and replay evolutionary decisions.

## Retention classes

Every learning artifact MUST have an explicit retention class:

- CORE_REQUIRED — required for current invariants or active behavior.
- REPLAY_REQUIRED — required to reconstruct a decision.
- PROVENANCE_REQUIRED — required to preserve origin/dependency.
- AUDIT_REQUIRED — required for immutable historical accountability.
- REFERENCE_ONLY — may be compacted behind an immutable content identifier.
- EXPIRED — no longer operationally relevant but retained according to audit policy.

No artifact may be deleted merely because it is old.

## Compaction invariant

Compaction MUST preserve semantic reconstructability:

CompactedHistory + ImmutableReferences -> EquivalentDecisionContext

Compaction MUST NOT change the meaning of a previously accepted/rejected decision.

## Content addressing

Large evidence may be stored through immutable content identifiers, hashes, or external archival references, provided integrity, provenance and retrieval status remain verifiable.

A hash alone is not evidence content; it proves identity/integrity only.

## Active rule protection

Artifacts referenced by active rules, unresolved governance decisions, open counterexamples, or pending re-evaluation MUST NOT be compacted beyond replay-safe representation.

## Partner repository retention

Each partner repository revision participating in learning receives an immutable revision identity. Later revisions do not overwrite historical learning dependencies.

## Deletion boundary

Deletion/expiry MUST be policy-governed and auditable. If deletion would prevent required replay or provenance verification, it is forbidden unless an explicit higher-level retention policy permits a documented non-replayable state.

## Acceptance

Tests must cover compaction/reconstruction equivalence, active-rule dependencies, open counterexamples, partner revision history, missing archival content, hash mismatch, restart/replay and retention-policy changes.

Status: DESIGNED / NOT_IMPLEMENTED.
