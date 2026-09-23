# E7.18 — Learned Rule Revocation, Rollback and Supersession Contract

## Objective

Ensure that a previously promoted learned rule can be safely suspended, revoked, rolled back, or superseded when later evidence invalidates its assumptions.

## Rule lifecycle

PROMOTION_CANDIDATE -> GOVERNED -> ACTIVE

Possible later transitions:

ACTIVE -> SUSPENDED
ACTIVE -> REVOKED
ACTIVE -> SUPERSEDED
ACTIVE -> ROLLED_BACK

SUSPENDED/REVOKED/SUPERSEDED rules MUST NOT execute as active rules.

## Trigger classes

A re-evaluation MAY be triggered by:

- new counterexample;
- source revision;
- source revocation;
- failed regression;
- invariant violation;
- authority/policy change;
- parent-state incompatibility;
- newly discovered provenance dependency;
- governance decision.

No trigger is itself proof of invalidity; it initiates controlled re-evaluation.

## Safe rollback

Rollback MUST create an auditable transition to a previously verified compatible state or a newly verified replacement.

Rollback MUST NOT delete:

- the promoted rule;
- its evidence;
- its governance decision;
- subsequent observations;
- counterexamples.

## Supersession

A replacement rule receives a new immutable revision and explicit parent/supersedes reference.

Historical revisions remain replayable as historical records but cannot silently regain active status.

## Revocation

Revocation MUST be fail-closed with respect to active execution. If execution is already in progress, the existing execution authorization boundary determines whether it may finish; revocation MUST NOT be treated as retroactive authorization.

## Acceptance

Tests must cover active->suspended, active->revoked, active->superseded, rollback, replacement, replay of revoked rules, stale replacement, and persistence/restart.

Status: DESIGNED / NOT_IMPLEMENTED.
