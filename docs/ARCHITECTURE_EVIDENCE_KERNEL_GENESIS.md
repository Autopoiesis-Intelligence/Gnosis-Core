# Target Repository Architecture — Evidence / Kernel / Genesis

**Status:** PROPOSED → migration baseline
**Date:** 2026-09-25
**Purpose:** establish the target architecture before any repository rename or destructive migration.

## Target model

Gnozis is the product/system identity. Its architecture is separated by trust, lifecycle and authority boundaries:

```
Gnozis
├── Evidence Plane
│   └── research, mathematics, provenance, experiments, historical context
│
├── Trusted Kernel
│   └── state, relations, transitions, evolution, verification, persistence,
│       audit and governance primitives
│
└── Genesis Factory
    └── bounded capability/module generation and product preparation
```

Canonical flow:

```
Evidence → Candidate → Test → Select → Evolve → Verify → Commit
                                                     ↓
                                                  Kernel
                                                     ↓
                                              Capability/Module
                                                     ↓
                                                  Product
```

## Repository target

- **Gnozis-Evidence** — machine-readable evidence/research plane.
- **Gnozis-Kernel** — minimal trusted operational plane.
- **Genesis** — protected factory/production mechanism. It may consume Kernel capabilities but is not granted automatic authority to mutate the Kernel.

The current repository **Genezis** is the protected engineering baseline that presently contains both the Kernel implementation and Genesis/factory material. This document does **not** claim that the physical split has already occurred.

## Trust rules

1. Evidence is input, not authority.
2. Research-memory/context is not equivalent to trusted Kernel state.
3. A proposal is not a transition.
4. A generated module is not automatically a Kernel capability.
5. Genesis cannot self-authorize Kernel mutation.
6. Verification evidence must be attributable to the exact artifact/version tested.
7. Repository boundaries follow trust, lifecycle and authority boundaries rather than directory aesthetics.

## Migration order

1. Freeze and document target boundaries.
2. Inventory current paths and classify each artifact.
3. Define machine-readable contracts between Evidence, Kernel and Genesis.
4. Separate logical namespaces before physical repository moves.
5. Move Evidence material to Gnozis-Evidence with provenance preserved.
6. Isolate the trusted Kernel from factory/product mechanisms.
7. Establish module/capability contracts.
8. Rename repositories only after references, CI, package metadata and provenance are reconciled.
9. Run structural → execution → causal verification.
10. Update public/product documentation only after evidence supports the resulting state.

## Forbidden during migration

- destructive history rewrite;
- silent deletion of historical evidence;
- treating documentation as implementation evidence;
- granting Genesis automatic authority over Kernel;
- introducing an LLM/AI model into the trusted Kernel;
- claiming repository names alone establish architectural separation.

## Current mapping

Current protected repository:
`Mikhail-Kucheriavyi-23/Genezis`

Current public repository:
`Mikhail-Kucheriavyi-23/Gnozis`

Target logical roles:
`Genezis` → protected engineering baseline containing **Kernel + Genesis** during transition.
`Gnozis` → public product/evidence surface during transition.
`Gnozis-Research-Memory` → transitional name for the evidence/context corpus until migration to **Gnozis-Evidence** is complete.

## Acceptance gate

This architecture is accepted only when:
- every current top-level component has one target owner;
- trust boundaries are represented in code/contracts;
- package/repository names agree with the logical roles;
- provenance survives migration;
- CI and tests reference the new locations;
- no historical claim is silently rewritten.
