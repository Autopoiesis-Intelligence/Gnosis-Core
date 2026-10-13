# Gnosis Contract Registry

Status: ACTIVE ARCHITECTURAL REGISTRY  
Snapshot date: 2026-10-13

This registry indexes declared contracts and observed repository boundaries. It does not grant authority or replace implementation contracts, CI, or runtime evidence. A contract is VERIFIED only when its required implementation, tests, exact-revision CI/runtime evidence, and acceptance conditions are present.

## Repository topology

Repository names and visibility below were observed from the connected GitHub organization on 2026-10-13. Roles are based on current repository contents and explicit documentation; a repository name alone does not establish its function or authority.

| Repository | Observed / declared role | Authority and boundary |
|---|---|---|
| Gnosis (public) | Public product and evidence surface | Product-code ownership versus Core-owned code remains unresolved |
| Gnosis-Core (public) | Canonical engineering repository for the active project workflow | Engineering contracts and implementation; relationship to private Gnosis-Genesis remains unresolved |
| Gnosis-Memory (public) | Research, formal material, provenance, and project-context collection | No execution authority inferred; canonical source-of-truth scope remains unresolved |
| Gnosis-Research (public) | Research and migration workspace suggested by current contents | Relationship to research material in Gnosis and Gnosis-Memory remains unresolved |
| Gnosis-Knowledge (public) | Repository exists; current root does not establish a stable role | Schema, ingestion contract, consumers, and authority are unconfirmed |
| Gnosis-SDK (public) | Repository exists; current root does not establish a stable role | Supported interfaces, consumers, versioning, and release scope are unconfirmed |
| Gnosis-Exchange (public) | Repository exists; current root does not establish a stable role | Product purpose and integration contract are unconfirmed |
| Thoth (private) | Private repository exists; role is not established by the current repository map | No dependency, execution, or authority boundary inferred from its name |
| Gnosis-Genesis (private) | Private repository exists; current root does not establish a production-factory role | Factory, production, deployment, and authority boundaries require explicit evidence and an owner decision |

Unconfirmed repositories must not be treated as implemented services or dependencies. Names in this table describe repository inventory, not accepted architecture.

## Execution order

1. Verify current-HEAD Core/P0 integrity against exact repository state.
2. Reconcile persistence, recovery, replay, and audit evidence.
3. Consolidate E7 contracts against production call paths.
4. Verify the Core mutation boundary.
5. Verify the Core integration boundary.
6. Verify reflection end to end.
7. Define governance, activation, and rollback contracts.
8. Resolve the Research/Memory ownership and migration boundary.
9. Establish the canonical mathematical corpus owner.
10. Accept a contract before implementing any specialized repository.
11. Implement only explicitly assigned modules.
12. Permit controlled autonomous learning only after all required gates are proven.

## Contract portfolio

The statuses below are inherited working labels and must be revalidated against the current exact revision. They are not claims of current CI or runtime success.

| ID | Contract | Working status | Primary repository / boundary |
|---|---|---|---|
| C0 | Core state and evolution | IMPLEMENTED / REVERIFY | Gnosis-Core |
| C1 | Persistence integrity | IMPLEMENTED / REVERIFY | Gnosis-Core |
| C2 | Recovery and replay | PARTIAL / REVERIFY | Gnosis-Core |
| C3 | Audit and provenance | IMPLEMENTED / REVERIFY | Gnosis-Core |
| C4 | E7 lifecycle integrity | IMPLEMENTED / CONSOLIDATE | Gnosis-Core |
| C5 | Core mutation boundary | IMPLEMENTED CANDIDATE / AUDIT | Gnosis-Core |
| C6 | Core integration boundary | IMPLEMENTED CANDIDATE / AUDIT | Gnosis-Core |
| C7 | Reflection evidence | IMPLEMENTED / UNVERIFIED | Gnosis-Core |
| C8 | Governance, activation, and rollback | MISSING / REVERIFY | Gnosis-Core |
| C9 | Research/context contract | PLANNED; ownership unresolved | Gnosis-Memory / Gnosis-Research — owner not accepted |
| C10 | Mathematical corpus | PLANNED; canonical owner unresolved | Gnosis-Memory / Gnosis-Research — owner not accepted |
| C11 | Knowledge schema and graph contract | UNASSIGNED | Gnosis-Knowledge — role not accepted |
| C12 | Observation and signal intake | UNASSIGNED | No primary repository accepted |
| C13 | Research/evidence contract | UNASSIGNED | Thoth exists as a private repository; role not accepted |
| C14 | Solution workflow contract | UNASSIGNED | No primary repository accepted |
| C15 | Module/product contract | UNASSIGNED | No primary repository accepted |
| C16 | Opportunity/market contract | PLANNED; ownership unresolved | Gnosis public surface versus other repositories not reconciled |
| C17 | SDK/interface/capability contract | UNASSIGNED | Gnosis-SDK — role not accepted |
| C18 | Public product/evidence surface | PLANNED / RECONCILE | Gnosis |
| C19 | Private factory/production boundary | UNVERIFIED / RECONCILE | Gnosis-Genesis; no production role inferred from repository name |

## Evidence rule

Documentation, source implementation, reachability, runtime evidence, persistence evidence, audit, and CI are separate evidence classes.

No registry entry may be promoted to VERIFIED solely because documentation or tests exist. A CI claim must identify the exact commit SHA and workflow run. A test PASS does not establish production reachability, runtime execution, persisted state, or authorization provenance.

## Current gate

The active engineering gate is current-revision Core integrity and trust-boundary verification. The relationship between public Gnosis, engineering Gnosis-Core, and private Gnosis-Genesis remains unresolved until supported by explicit implementation evidence and an accepted boundary decision.

New repository implementation is contract-first and must not bypass the current Core acceptance gates.
