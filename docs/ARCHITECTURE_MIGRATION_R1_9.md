# Gnozis-V2 — Architecture Migration R1.9

## Purpose

This document is the implementation manifest for the R1.9 repository restructuring.

The migration is incremental. Existing working mechanisms are preserved until their semantics are mapped to the target architecture and verified after movement.

## Repository roles

- **Gnozis-V2** — canonical evolving runtime/Core.
- **Gnozis** — temporary development/research archive and external engineering memory.

Gnozis-V2 is the only canonical runtime state/evolution authority.

## Target Core

The following responsibilities remain inside the Core:

- Ψ=(X,R) canonical state;
- deep immutability and integrity;
- protected transitions;
- memory semantics;
- analysis;
- reflection;
- evolution;
- verification;
- governance;
- authorization;
- autopoiesis;
- sandbox;
- sentinel;
- runtime coordination.

## Boundary model

`gnosis/ports/` defines protected contracts.

`gnosis/adapters/` contains replaceable external implementations.

Core semantics must not depend on concrete adapters.

Persistence remains Core-adjacent through a port/adapter boundary; SQLite implementation stays outside semantic Core.

## Development archive boundary

The archive stores machine-readable engineering memory: AI context, task definitions, audits, research findings, migration records, and historical implementation evidence.

Archive contents do not become runtime truth merely by being stored.

## Migration rule

For every existing module: identify current semantics; map to target responsibility; preserve behavior unless a defect is demonstrated; move only when dependencies are understood; run tests; audit authority/provenance boundaries; remove obsolete duplicate paths only after verification.

## Defect routing

A defect that changes canonical runtime semantics is fixed in **Gnozis-V2**.

A research observation, unresolved hypothesis, or development-process issue that can be investigated without changing canonical runtime semantics is recorded in the **Gnozis development archive**.

If the runtime demonstrates a defect that Gnozis can safely diagnose but cannot autonomously repair under current authority, the finding is archived as a bounded development task.

## Hard boundaries

- No second canonical Ψ model.
- No direct external mutation of Core state.
- No autonomous activation bypassing verification/governance/authorization.
- Sandbox remains inside Core.
- Analysis and autopoiesis remain inside Core.
- Development archive is not runtime memory.
- Documentation is not evidence of execution.

## Migration state

Phase M0 — inventory and semantic mapping: **IN PROGRESS**.

No existing runtime module is deleted solely because it does not yet match the target directory name.
