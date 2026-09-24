# E8.02 — Evidence-Gated Contract Formation & Routing

## Objective
Form the appropriate contract candidate from an evidence-backed opportunity without allowing classification to become execution authority.

## Routing
- LOW_RELEVANCE → GENERAL_OPEN
- RESEARCH_RELEVANT → RESEARCH_LEGAL
- COMMERCIAL → COMMERCIAL_PARTNER

Commercial formation requires explicit financial evidence and a `partner:` scope. Research formation is legally/research relevant but does not imply a financial component. A non-commercial opportunity cannot silently become commercial merely because financial metadata is attached.

## Invariants
Every candidate has evidence, explicit scope, value level and status. Only ADMITTED candidates may be issued. Contract formation never grants execution authority.

## Status
PARTIAL / UNVERIFIED.
