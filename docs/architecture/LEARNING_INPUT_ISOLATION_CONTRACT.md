# E7.99 — Learning Input Provenance & Evidence Isolation

## Objective
Bind every learning input to its source, evidence, learning scope and confidentiality class so general, Core-private and partner-private experience cannot be silently mixed.

## Invariants
Only ADMITTED inputs with evidence may enter learning. PARTNER_PRIVATE inputs cannot cross into another scope. Every input has a deterministic provenance digest. Isolation is enforced by scope metadata, not by naming conventions.

## Status
PARTIAL / UNVERIFIED.
