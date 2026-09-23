# E7.34 — Partner Evidence Retention & Privacy Boundary

## Objective
Separate immutable evidence facts from private payload retention so privacy operations never rewrite historical evidence.

## Model
Evidence = ImmutableFact + ControlledPayload + Provenance

Private payload MAY expire, be redacted or deleted independently of the historical event.

Delete(Payload) != Delete(Event)
Redact(Payload) != Rewrite(History)

Retention decisions MUST identify subject, policy revision, action, reason and effective state. Privacy operations MUST themselves be auditable.

After payload deletion/redaction, approved integrity/provenance references MAY remain where policy permits. Secrets, credentials and unnecessary private payload MUST NOT be copied into ordinary audit evidence.

Expired/deleted payload MUST NOT become available again through replay, old packages or restart recovery.

Partner privacy and cross-partner scope isolation remain mandatory.

## Acceptance tests
Retention expiry; redaction; deletion; reference preservation; replay after deletion; restart/recovery; privacy event audit; no secret persistence; cross-partner isolation; no resurrection.

## Status
DESIGNED / NOT_IMPLEMENTED
