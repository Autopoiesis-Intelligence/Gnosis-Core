# R2.DOC-2 — Repository Information Synchronization Contract

## Purpose
Keep repository-facing information synchronized with verified implementation without allowing documentation to become a false source of truth.

## Canonical hierarchy
Code + Tests + Runtime Evidence + Immutable Commit are authoritative for implementation claims.
AI_CONTEXT.md, STATUS.md, AUDIT.md, README, and public architecture descriptions are derived projections.

Documentation does not imply Implementation.
DocumentationConflict -> Reconciliation.

## Required repository surfaces
After every material architectural change, determine whether it affects: implementation; tests/CI evidence; AI_CONTEXT; STATUS; AUDIT; architecture/contracts; README/public description; machine-readable project context.
Only affected surfaces are updated; cosmetic synchronization is not required.

## Information update record
Every synchronization event MUST identify: update_id; source commit/revision; affected contract IDs; affected repository surfaces; previous documented status; new documented status; implementation evidence; verification evidence; unresolved gaps; timestamp; agent/operator identity.

## Status discipline
Implementation states: IMPLEMENTED | PARTIAL | MISSING | THEORETICAL | BLOCKED.
Verification states: VERIFIED | UNVERIFIED | BLOCKED | NOT_APPLICABLE.
Documentation MUST NOT upgrade implementation or verification state without corresponding evidence.
IMPLEMENTED requires implementation evidence and, where executable behavior is claimed, execution/test evidence.

## Commit binding
Claims about current repository state MUST be bound to an immutable commit SHA. A branch name alone is insufficient.
If documentation refers to an older snapshot, it MUST be marked historical/stale.

## Conflict handling
When code, tests and documentation disagree: preserve the discrepancy; identify the authoritative source; open a reconciliation task/contract; do not silently rewrite history; update derived documentation only after classification.

## External and partner information
Partner repositories, external audits and agent submissions are evidence sources, not implementation authority. External claims preserve source identity, source revision, provenance and audit scope. Consensus between external sources does not by itself establish truth.

## Update triggers
A synchronization pass SHOULD run after accepted implementation changes, contract status changes, independent audit findings, CI result changes, schema/persistence changes, trust-boundary changes, agent/partner onboarding, public capability changes, repository restructuring, or discovery of documentation drift.

## Acceptance invariant
CurrentDescription = Projection(VerifiedRepositoryState) within the declared documentation scope.
If the projection cannot be established, documentation MUST expose uncertainty instead of inventing completeness.

## Parallel repository principle
For multiple repositories, each repository maintains its own immutable source state and local evidence. Cross-repository descriptions MUST identify repository + commit + contract + evidence scope.
A repository must never be described as implemented merely because another repository contains the corresponding design.

## Completion
The contract is complete only when a machine-readable synchronization record can be generated, reviewed, and traced from a repository commit to every changed project-information surface.

Status: DESIGNED / NOT_IMPLEMENTED.