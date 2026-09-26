# Genesis Audit — Root Inventory

Audit phase: structural, read-only classification.

Observed root boundaries:
- gnosis/ — primary implementation namespace; requires module-by-module classification.
- context/ — context continuity material; candidate for Product interface and/or Research-Memory depending on sensitivity.
- diagnostic_corpus/ — diagnostic/evidence corpus; private Genesis unless a sanitized public subset is explicitly published.
- registry/ — registry boundary; classify by whether it contains capabilities, modules, evidence, or private routing.
- tests/ — evidence boundary; retain with the implementation they prove.
- docs/ — documentation; split public contracts from private implementation documentation.
- .github/ — CI/evidence automation; retain where it protects private Genesis, but expose only public workflows that are safe.
- logs/ — operational data; treat as sensitive and do not migrate into public repositories by default.
- AI_CONTEXT.md and STATUS.md — durable developer/context records; preserve as evidence/context, but do not make them the product runtime memory.
- AUDIT.md — audit evidence; preserve with provenance.
- commercial/research license and trademark documents — legal/product boundary; retain in the private repository unless a public-facing license document is intentionally published.

## Immediate rule

Do not move or delete any Genesis root directory during this phase.

The next audit must inspect the gnosis/ namespace and classify concrete modules by dependency direction, trust level, data sensitivity, and intended public interface.

## Important distinction

Directory names are not proof of architectural responsibility. Final placement is decided from code behavior and dependencies, not names.
