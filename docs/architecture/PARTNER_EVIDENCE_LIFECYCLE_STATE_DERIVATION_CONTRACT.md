# E7.35 — Partner Evidence Lifecycle & State Derivation Contract

## Objective
Define one deterministic lifecycle model joining audit, dispute, correction, retention, privacy and revocation without competing state authorities.

## Identity
Evidence identity is bound to content digest, provenance, source revision and contract revision. Content changes create a new evidence object.

## History vs current state
HistoricalState(e) != CurrentState(e)

Current state is derived from authoritative history plus applicable policy/revision state:

State_t(e) = F(History_<=t(e), Policy_t, Contract_t, Revocation_t, Retention_t)

Thus an evidence object may historically be ADMITTED while currently REVOKED and its payload REDACTED.

Corrections append new events. Revocation changes current usability without deleting history. Retention changes payload availability without fabricating non-existence.

## Conflict handling
If audit, registry, runtime or another authoritative source disagree, the conflict MUST become an explicit finding and protected actions MUST follow the applicable fail-closed rule. No arbitrary last-writer-wins state may be used.

Replay of historical valid context MUST NOT resurrect revoked, expired or deleted state without an explicitly permitted new procedure.

## Acceptance tests
Normal lifecycle; admission/revocation; dispute/correction; retention expiry; payload deletion/redaction; replay resistance; conflicting sources; deterministic reconstruction; restart/recovery; audit continuity; no authority escalation; no resurrection.

## Status
DESIGNED / NOT_IMPLEMENTED
