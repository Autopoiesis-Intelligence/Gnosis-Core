# Repository Migration Map — Initial Classification

**Date:** 2026-09-25
**Status:** INVENTORY-1 / NOT YET MIGRATED
**Rule:** classification is provisional until each artifact is checked for imports, authority, lifecycle and provenance.

## Target repositories

| Current location | Target role | Target repository | Status |
|---|---|---|---|
| `Genezis/gnosis/core` | Trusted state/evolution kernel | Gnozis-Kernel | KERNEL |
| `Genezis/gnosis/storage` | Durable state/provenance persistence | Gnozis-Kernel | KERNEL |
| `Genezis/gnosis/instances` | Kernel instance/lineage semantics | Gnozis-Kernel | KERNEL |
| `Genezis/gnosis/evolution` | Evolution transition machinery | Gnozis-Kernel | KERNEL |
| `Genezis/gnosis/control` | Governance/control boundary | Gnozis-Kernel | KERNEL / REVIEW |
| `Genezis/gnosis/reflection` | Observation/evidence generation | Kernel-adjacent; final placement after dependency audit | REVIEW |
| `Genezis/gnosis/self_learning` | Learning/factory orchestration | Genesis | REVIEW |
| `Genezis/gnosis/context` | Context/evidence ingestion | Gnozis-Evidence or interface layer | REVIEW |
| `Genezis/diagnostic_corpus` | Protected diagnostic test corpus | Gnozis-Kernel | KERNEL |
| `Genezis/logs` | Runtime/audit evidence | Gnozis-Kernel | KERNEL / REVIEW |
| `Genezis/context` | Machine-readable project/evidence context | Gnozis-Evidence | EVIDENCE |
| `Genezis/docs` | Mixed architecture/contracts/hand-off docs | split by authority | REVIEW |
| `Genezis/scripts` | Build/contract/partner tooling | split by lifecycle | REVIEW |
| `Gnozis/research` | Research records and experiments | Gnozis-Evidence | EVIDENCE |
| `Gnozis/research_machine` | Machine-readable evidence/contracts | Gnozis-Evidence | EVIDENCE |
| `Gnozis/AI_CONTEXT.md` | Historical/context corpus | Gnozis-Evidence | EVIDENCE |
| `Gnozis/RESEARCH_SOURCES.md` | Research provenance | Gnozis-Evidence | EVIDENCE |
| `Gnozis/PHILOSOPHY.md` | Research/philosophical source material | Gnozis-Evidence | EVIDENCE |
| `Gnozis/README.md` | Public product surface | Gnozis | PUBLIC |

## Important finding

The current protected repository already contains a recognizable Kernel boundary under `gnosis/core`, but the repository also contains reflection, self-learning, context and tooling with different trust/lifecycle roles.

Therefore the next step is **logical separation**, not an immediate GitHub rename.

## Required checks before physical movement

For every REVIEW item:
1. imports/dependency direction;
2. writes to Kernel state;
3. authorization authority;
4. persistence/provenance responsibility;
5. test ownership;
6. external data boundary;
7. whether it is reusable Kernel mechanism or factory/product-specific behavior.

## Migration invariant

No file moves from one repository to another until its source commit, provenance and target ownership can be reconstructed.

## Naming transition

The old names remain valid historical identifiers:

- `Genezis` = current protected engineering repository.
- `Gnozis` = current public repository.
- `Gnozis-Research-Memory` = transitional conceptual name.

Target names:

- `Gnozis-Kernel`
- `Gnozis-Evidence`
- `Genesis` as protected factory/product-generation role.

A historical repository name must never be rewritten in a way that destroys provenance.
