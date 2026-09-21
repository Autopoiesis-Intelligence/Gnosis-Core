# Gnozis-V2 — R1 Repository Classification Map

Status: ACTIVE
Baseline: architecture/restructure-r1-9

| Area | Target | Authority | Migration state |
|---|---|---|---|
| gnosis/core/ | Core | canonical Ψ/invariants | KEEP |
| gnosis/evolution/ | Core | governed evolution | KEEP |
| gnosis/storage/ | Core | canonical durable state/audit | KEEP |
| gnosis/instances/ | Core | lineage/instance semantics | KEEP |
| gnosis/reflection/ | Core | bounded analytical runtime | KEEP |
| gnosis/context/ | Core interface | task/user continuity | KEEP, boundary extracted |
| tests/ | Core | executable evidence | KEEP |
| .github/ | Core | CI/tooling | KEEP |
| current contracts/docs | Core interface | operational authority | KEEP |
| AI_CONTEXT.md | Research Machine input | development continuity | MIGRATION CANDIDATE |
| diagnostic_corpus/ | Research Machine | experimental evidence | FIRST EXTRACTION |
| logs/audit/ | Research Machine | historical evidence | DEFERRED |
| historical/rejected analyses | Research Machine | research provenance | MOVE |
| archive/ | neither | transitional only | DO NOT EXPAND |
| LICENSE/LEGAL | Core/project | legal authority | KEEP |

## Rules

1. Classification follows authority and runtime responsibility, not filename.
2. Core must execute without the Research Machine repository.
3. Research Machine cannot mutate canonical Core state directly.
4. Research input becomes an explicit typed input/evidence reference before Core admission.
5. Moving records preserves source commit, identity, provenance, verification status and destination reference.
6. No third repository is created for temporary state.
7. The Core sandbox remains inside Core.
8. Core analytical layers, autopoiesis and memory remain inside Core.
9. Core may acquire additional internal capabilities when demonstrated conditions require them, with bounded contracts and executable verification.
10. Physical migration begins only after the receiving Research Machine contract exists.

## Current conclusion

The semantic split is sufficiently established to begin the first controlled extraction: diagnostic_corpus.

The extraction must be reversible and provenance-preserving. No deletion from Core is permitted in this stage.
