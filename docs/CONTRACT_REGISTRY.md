# Gnozis Contract Registry

Status: ACTIVE ARCHITECTURAL REGISTRY
Date: 2026-09-25

This registry is the orchestration index for the current Gnozis repository architecture. It does not replace implementation contracts or runtime evidence. A contract becomes VERIFIED only when its required implementation, tests, CI/runtime evidence and acceptance conditions are present on the relevant canonical revision.

## Repository topology

| Repository | Role | Authority |
|---|---|---|
| Gnozis | Public research/evidence/opportunity surface | Public presentation only |
| Gnozis-Research-Memory | Machine-readable research, mathematics, provenance and context | No Core mutation authority |
| Mnemosyne | Knowledge / relations / evidence graph | No Core mutation authority |
| Hermes | Discoveries / signals / observation intake | No Core mutation authority |
| Thoth | Research / experiments / evidence | No Core mutation authority |
| Athena | Solutions / solution workflows | No Core mutation authority |
| Hephaestus | Modules / products / marketplace outputs | No Core mutation authority |
| Prometheus | Opportunities / market pipeline | No Core mutation authority |
| Daedalus | CLI / MCP / API / SDK interface boundary | Capability-scoped access only |
| Genesis / Genezis | Protected Core + Module Factory | Governed engineering authority |
| Uroboros | Core evolutionary mechanism | Bounded by Genesis trust/governance contracts |

## Execution order

1. Current-HEAD Core/P0 integrity verification
2. Persistence/recovery/replay/audit reconciliation
3. E7 contract consolidation
4. Core mutation boundary verification
5. Core integration boundary verification
6. Reflection end-to-end verification
7. Governance / activation / rollback contract
8. Research-Memory separation and migration
9. Canonical mathematical corpus
10. Contract each new specialized repository
11. Implement specialized modules
12. Controlled autonomous learning only after all required gates

## Contract portfolio

| ID | Contract | Initial status | Primary repository |
|---|---|---|---|
| C0 | Ψ-Core state/evolution | IMPLEMENTED / REVERIFY | Genesis / Uroboros |
| C1 | Persistence integrity | IMPLEMENTED / REVERIFY | Genesis |
| C2 | Recovery / replay | PARTIAL / REVERIFY | Genesis |
| C3 | Audit / provenance | IMPLEMENTED / REVERIFY | Genesis |
| C4 | E7 lifecycle integrity | IMPLEMENTED / CONSOLIDATE | Genesis |
| C5 | Core mutation boundary | IMPLEMENTED CANDIDATE / AUDIT | Genesis |
| C6 | Core integration boundary | IMPLEMENTED CANDIDATE / AUDIT | Genesis |
| C7 | Reflection evidence | IMPLEMENTED / UNVERIFIED | Genesis |
| C8 | Governance / activation / rollback | MISSING | Genesis |
| C9 | Research-Memory contract | PLANNED | Gnozis-Research-Memory |
| C10 | Mathematical corpus | PLANNED | Gnozis-Research-Memory |
| C11 | Knowledge graph contract | PLANNED | Mnemosyne |
| C12 | Discovery/signal contract | PLANNED | Hermes |
| C13 | Research/evidence contract | PLANNED | Thoth |
| C14 | Solution contract | PLANNED | Athena |
| C15 | Module/product contract | PLANNED | Hephaestus |
| C16 | Opportunity/market contract | PLANNED | Prometheus |
| C17 | Interface/capability contract | PLANNED | Daedalus |
| C18 | Public Gnozis surface contract | PLANNED | Gnozis |
| C19 | Module Factory contract | PLANNED / bounded | Genesis |

## Evidence rule

Documentation, source, tests, CI, runtime evidence and independent audit are distinct evidence classes.

No registry entry may be promoted to VERIFIED solely because documentation or tests exist.

## Current gate

The active engineering gate is the Genesis/Genezis P0 runtime and trust-boundary verification. New repository implementation is contract-first and must not bypass the current Core acceptance gates.
