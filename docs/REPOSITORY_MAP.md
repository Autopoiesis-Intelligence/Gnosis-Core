# Repository Map — Evidence-Based Snapshot

**Snapshot date:** 2026-10-13  
**Purpose:** distinguish observed repository contents from intended roles and unresolved ownership boundaries.  
**Authority rule:** this map records observations; it does not itself grant implementation or execution authority. Recheck default-branch refs before relying on any SHA.

## Repositories

| Repository | Visibility | Observed root / declared role | Current classification | Unresolved boundary |
|---|---|---|---|---|
| [Gnosis](https://github.com/Autopoiesis-Intelligence/Gnosis) | Public | README declares a public product, opportunities, and evidence surface; root contains application code, tests, contracts, research, provenance, and tools. | Public product/evidence repository (declared); contains more than a static presentation layer. | Exact division of product code versus Core-owned code is not established by the README alone. |
| [Gnosis-Core](https://github.com/Autopoiesis-Intelligence/Gnosis-Core) | Public | README calls this the canonical engineering foundation, but also says it is “currently operated as Genesis/Genezis”; root contains `gnosis/`, tests, context, docs, registry, scripts, and tools. | Current canonical engineering repository for the active project workflow. | Its relationship to the separate private `Gnosis-Genesis` repository is unresolved. Do not equate the two based on historical wording. |
| [Gnosis-Memory](https://github.com/Autopoiesis-Intelligence/Gnosis-Memory) | Public | Root contains architecture/product documents, contracts, formal material, provenance, historical material, and research directories. README on main remains only `# Mnemosyne`. | Research/context/document collection (observed contents; intended source-of-truth scope not yet accepted). | `AI_CONTEXT.md` is byte-identical to the copy in `Gnosis` at the observed refs. Decide whether this duplication is intentional and which repository, if either, owns the canonical version. |
| [Gnosis-Genesis](https://github.com/Autopoiesis-Intelligence/Gnosis-Genesis) | Private | Current `main` root contains only `.gitkeep`; no README was found. Other repository documentation describes Genesis as a protected production factory. | Intended role is documented elsewhere, but not established by this repository's current root contents. | Factory, authority, deployment, and source-code boundaries require an explicit owner decision. |
| [Gnosis-Exchange](https://github.com/Autopoiesis-Intelligence/Gnosis-Exchange) | Public | Current `main` root contains only `.gitkeep`; no README was found. | Placeholder / role unconfirmed. | Product purpose, dependencies, and source-of-truth scope not documented in the inspected root. |
| [Gnosis-SDK](https://github.com/Autopoiesis-Intelligence/Gnosis-SDK) | Public | Current `main` root contains only `.gitkeep`; no README was found. | Placeholder / role unconfirmed. | Supported interface, consumers, versioning, and release scope not documented in the inspected root. |
| [Gnosis-Research](https://github.com/Autopoiesis-Intelligence/Gnosis-Research) | Public | Root contains `.gitkeep`, `MIGRATION/`, and `SELF-DIAGNOSTIC-0001/`; no README was found. | Research/migration work area suggested by directory names; no accepted full role statement found at root. | Relationship to the research material in `Gnosis` and `Gnosis-Memory` is unresolved. |
| [Gnosis-Knowledge](https://github.com/Autopoiesis-Intelligence/Gnosis-Knowledge) | Public | Root contains `.gitkeep` and a README consisting only of `# Prometheus`. | Placeholder / role unconfirmed. | Knowledge schema, ingestion contract, consumers, and authority are not documented in the inspected root. |

## Default-branch references observed

These are point-in-time `main` commit refs resolved on 2026-10-13, not CI or runtime evidence.

| Repository | Observed `main` SHA |
|---|---|
| `Gnosis` | `93f045f562e93e2f0fa74b42a711ec59b5b570da` |
| `Gnosis-Core` | `6eed57dbbae1778039f1c2db67ab6a17b3ca091a` |
| `Gnosis-Memory` | `7d1b97ccea2febead512b5c0ff2905d038d7bb3a` |
| `Gnosis-Exchange` | `f2f2d118706311e174672095c1430db75851e9a6` |
| `Gnosis-SDK` | `f508bfe45109ba7bb7c3a00b3f2a625798d9a4cd` |
| `Gnosis-Research` | `9574420c8868f302d7628c731ee63b9a6ab868c4` |
| `Gnosis-Knowledge` | `2ce0fda215a2318072ef68b214e7967cffa781de` |
| `Gnosis-Genesis` (private) | `8f3d482ad4f533e685860b4824b49bdecb4c5c0f` |

## GitHub repository-description snapshot

Descriptions observed from repository metadata on 2026-10-13. These are current metadata strings, not accepted architecture.

| Repository | Current GitHub description | Assessment |
|---|---|---|
| `Gnosis` | `Universal scientific discovery platform powered by UROBOROS — Ψ-Core v33: a recursive, naturally autopoietic computational core for modeling, AI, reasoning, simulation, research and discovery.` | Does not clearly match the README's stated public product/evidence-surface role; the description appears to present the Core as the repository's main identity. |
| `Gnosis-Core` | `next realize ` | Not an informative repository description. |
| `Gnosis-Memory` | None | Missing. |
| `Gnosis-Exchange` | None | Missing. |
| `Gnosis-SDK` | None | Missing. |
| `Gnosis-Research` | None | Missing. |
| `Gnosis-Knowledge` | None | Missing. |
| `Gnosis-Genesis` (private) | None | Missing; do not infer the private repository's role from the absence of a description. |

**Decision:** do not edit these descriptions until the owner resolves the `Gnosis` / `Gnosis-Core` / `Gnosis-Genesis` role boundary and the canonical owner of duplicated project context. Once the role map is accepted, descriptions can be normalized as a single bounded documentation task.

## Operating rules

1. **Observed contents are not accepted architecture.** Names, README claims, and directory names are clues, not proof of role or authority.
2. **No cross-repository canonicality by duplication.** Identical files in multiple repositories do not establish which copy is authoritative.
3. **No invented dependency graph.** Record dependencies only after finding explicit imports, workflows, package references, contracts, or an accepted architecture decision.
4. **No automatic cleanup.** Do not delete, move, or rewrite repositories or shared documents to make the map look consistent before the owner resolves the ambiguities.
5. **Evidence stays layered:** DESIGN → IMPLEMENTED → REACHABLE → RUNTIME → PERSISTED → AUDITED → CI_PROVEN. A commit SHA proves which snapshot was observed, not that it passes.
6. **Private/public boundaries matter.** Do not publish private implementation details or scratchpad contents in public repositories.

## Decisions needed from the project owner

- Define the boundary between public `Gnosis`, engineering `Gnosis-Core`, and private `Gnosis-Genesis`.
- Decide whether the shared `AI_CONTEXT.md` in `Gnosis` and `Gnosis-Memory` is intentional; if not, identify the canonical owner before changing either copy.
- Assign explicit roles and consumers for `Gnosis-Exchange`, `Gnosis-SDK`, `Gnosis-Research`, and `Gnosis-Knowledge`.
- Only after these decisions, align GitHub descriptions and README openings. Do not infer CI or runtime readiness from this map.
