# Gnosis Contract Registry

Status: ACTIVE ARCHITECTURAL REGISTRY
Date: 2026-09-25

This registry is the orchestration index for the current Gnosis repository architecture. It does not replace implementation contracts or runtime evidence. A contract becomes VERIFIED only when its required implementation, tests, CI/runtime evidence and acceptance conditions are present on the relevant canonical revision.

## Repository topology

| Repository | Role | Authority |
|---|---|---|
| Gnosis | Public product and evidence surface | Public presentation of selected, appropriate results; no Core authority |
| Gnosis-Core | Canonical authority-bearing runtime | Sole authority for accepted canonical state transitions |
| Gnosis-Genesis | Protected module factory and orchestration layer | May propose candidates and call explicit Core contracts; no independent canonical state authority |
| Gnosis-Memory | Research, mathematics, provenance and context | Evidence/input only; no Core mutation authority |
| Gnosis-Research | Research and diagnostic evidence workspace | No Core mutation authority |
| Gnosis-Knowledge | Knowledge-related workspace; detailed scope remains unresolved | No implicit Core mutation authority |
| Gnosis-Exchange | Detailed role not yet accepted | Unassigned; no authority inferred from name |
| Gnosis-SDK | Interface/SDK boundary | Capability-scoped access only |


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
| C0 | Ψ-Core state/evolution | IMPLEMENTED / REVERIFY | Gnosis-Core |
| C1 | Persistence integrity | IMPLEMENTED / REVERIFY | Gnosis-Core |
| C2 | Recovery / replay | PARTIAL / REVERIFY | Gnosis-Core |
| C3 | Audit / provenance | IMPLEMENTED / REVERIFY | Gnosis-Core |
| C4 | E7 lifecycle integrity | IMPLEMENTED / CONSOLIDATE | Gnosis-Core |
| C5 | Core mutation boundary | IMPLEMENTED CANDIDATE / AUDIT | Gnosis-Core |
| C6 | Core integration boundary | IMPLEMENTED CANDIDATE / AUDIT | Gnosis-Core |
| C7 | Reflection evidence | IMPLEMENTED / UNVERIFIED | Gnosis-Core |
| C8 | Governance / activation / rollback | MISSING | Gnosis-Core |
| C9 | Research-Memory contract | PLANNED | Gnosis-Memory |
| C10 | Mathematical corpus | PLANNED | Gnosis-Memory |
| C11 | Knowledge graph contract | PLANNED | Gnosis-Knowledge (scope unresolved) |
| C12 | Discovery/signal contract | PLANNED | UNASSIGNED — repository mapping unresolved |
| C13 | Research/evidence contract | PLANNED | Gnosis-Research |
| C14 | Solution contract | PLANNED | UNASSIGNED — repository mapping unresolved |
| C15 | Module/product contract | PLANNED | UNASSIGNED — repository mapping unresolved |
| C16 | Opportunity/market contract | PLANNED | UNASSIGNED — repository mapping unresolved |
| C17 | Interface/capability contract | PLANNED | Gnosis-SDK |
| C18 | Public Gnosis surface contract | PLANNED | Gnosis |
| C19 | Module Factory contract | PLANNED / bounded | Gnosis-Genesis |

## Evidence rule

Documentation, source, tests, CI, runtime evidence and independent audit are distinct evidence classes.

No registry entry may be promoted to VERIFIED solely because documentation or tests exist.

## Current gate

The active engineering gate is Gnosis-Core P0 runtime and trust-boundary verification. Gnosis-Genesis factory integration remains separately unproven. New repository implementation is contract-first and must not bypass current Core acceptance gates.
