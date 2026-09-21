# R1.9 — Dependency and Mutation Boundary Audit

## Confirmed facts from source inspection

### Canonical state
`gnosis/core/types.py` contains the frozen `State` model, deep-freezing of mappings/sequences, and stable state/content digests.

`gnosis/core/evolution.py` contains `Engine` and the current evolution lifecycle. The engine replaces its runtime-held state reference after an accepted candidate; the canonical `State` object itself remains frozen.

### Sandbox
`gnosis/evolution/sandbox.py` is already a bounded child-process sandbox. It returns evidence and explicitly does not cross Engine, persistence, or activation handles.

Therefore the target requirement 'Sandbox remains inside Core' is already substantially implemented semantically. We must not move it outside the Core merely to satisfy directory naming.

### Persistence
`gnosis/storage/` owns concrete SQLite implementation. `gnosis/evolution/transaction.py` directly imports sqlite3.

This confirms that persistence is currently coupled at implementation level. The correct migration is to introduce a persistence contract and then adapt callers, not to move SQLite files blindly.

### Reflection
`gnosis/reflection/` contains runtime reflection, evidence, counterexamples, proposals, governance and authority boundaries.

`gnosis/reflection/runtime.py` documents reflection as read-only with respect to canonical Core and persists reflection evidence.

`gnosis/reflection/authority.py` explicitly fails closed and currently does not provide an owner-authority issuer. This is an important boundary, not a defect to bypass.

### Context
`gnosis/context/` contains durable `TaskContext` and context reconstruction/handoff. It uses SQLite directly.

This is a mixed boundary: some context is runtime capability/context, while development AI_CONTEXT is external engineering memory. They must not be conflated.

## Current architectural finding

The repository already contains most target capabilities. The migration should therefore proceed by boundary extraction and semantic consolidation, not by wholesale directory relocation.

## First safe physical migration

The first concrete code migration should be a PersistencePort contract around the existing storage implementation.

Do not yet move `gnosis/storage/`.

Required sequence:

1. define the minimum persistence protocol required by Core;
2. provide an adapter over existing SQLite repositories;
3. add contract tests;
4. replace one direct consumer at a time;
5. verify regression/CI;
6. only then consider physical relocation.

## Mutation boundary findings

Known mutation surfaces requiring explicit audit:

- `Engine.state` replacement after accepted evolution;
- persistent transition writes;
- reflection persistence;
- context repository updates;
- authority/commit paths;
- instance/clone/fork creation.

The migration must prove that none of these creates a second canonical state authority.

## Next gate

Create the minimal persistence port without changing runtime behavior.

Acceptance:

- current SQLite behavior preserved;
- no semantic Core change;
- direct SQLite dependency reduced only where covered by the port;
- contract tests prove equivalence;
- failure/recovery/hash-chain tests remain valid.
