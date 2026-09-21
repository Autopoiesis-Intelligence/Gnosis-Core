# Gnozis-V2 — R1.9 Current → Target Inventory

## Baseline

Inventory is based on the current repository branch at the start of R1.9 migration. Existing implementation is not assumed to match the target naming.

## Current semantic areas

| Current path | Current role | R1.9 decision |
|---|---|---|
| gnosis/core/ | canonical Ψ/state/invariants/evolution primitives | KEEP as protected semantic Core |
| gnosis/evolution/ | transition, transaction, sandbox, recovery, provenance/audit machinery | KEEP Core-adjacent; map selectively into core/runtime, core/sandbox, ports/adapters without premature movement |
| gnosis/storage/ | SQLite persistence, repositories, durable evolution memory | KEEP Core-adjacent; move behind persistence port only after contract tests |
| gnosis/instances/ | instance, clone, lineage semantics | KEEP; later map to agent/instance capability boundaries |
| gnosis/reflection/ | findings, counterexamples, proposals, shadow evaluation, governance/authority support | KEEP semantically inside Core; do not relocate until dependency graph is verified |
| gnosis/context/ | TaskContext, snapshots, handoff, context repository | KEEP outside canonical Ψ; candidate bridge to development archive and runtime task/context layer |
| diagnostic_corpus/ | diagnostic/research material | KEEP outside Core |
| tests/ | executable evidence | KEEP; reorganize only after migration paths are stable |
| logs/ | audit/review artifacts | KEEP outside semantic Core |
| docs/ | architecture/contracts/audits | KEEP as development memory |
| formal/ | formal research/proof artifacts | KEEP outside runtime semantic Core unless a specific verified bridge is established |

## Target semantic placement

### Remains inside Core

- Ψ=(X,R)
- integrity/invariants
- protected transition semantics
- memory semantics
- analysis
- reflection
- evolution
- verification
- governance
- authorization
- autopoiesis
- sandbox
- sentinel
- runtime coordination

### Remains outside semantic Core

- concrete SQLite implementation
- network/filesystem/model/vendor adapters
- development archive
- AI_CONTEXT
- audit documents
- formal research artifacts
- test infrastructure

## Immediate finding

The existing repository already contains much of the target semantic machinery. Therefore R1.9 is primarily a boundary and consolidation migration, not a greenfield rewrite.

In particular, gnosis/reflection/, gnosis/evolution/, gnosis/storage/, gnosis/instances/, and gnosis/context/ must not be mechanically moved just to match directory names.

## First migration gate

Before moving any existing implementation:

1. establish import/dependency graph;
2. identify canonical state owners;
3. identify all mutation paths;
4. identify all persistence paths;
5. identify all reflection → proposal → governance paths;
6. identify all external boundary paths;
7. run current regression/CI evidence;
8. then move one bounded semantic slice at a time.

## Defect routing

Runtime-semantic defects → fix in Gnozis-V2.

Research/process/context defects → record in Development Archive.

Autonomous repair candidates → archive as bounded findings first; activate only through existing Core authority controls.

## Current state

M0 inventory: IN PROGRESS.

No destructive moves are authorized by this inventory alone.
