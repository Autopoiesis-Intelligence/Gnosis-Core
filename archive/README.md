# Gnozis Archive

## Purpose

Gnozis Archive is the historical, research and evidence-preservation layer of the Gnozis project.
It is not a second Core and it is not an authority source for Gnozis-Core.

Architectural direction:

Gnozis-Core → export boundary → Gnozis Archive

The Archive may preserve research records, evolution history, snapshots, summaries and machine-readable evidence. Archive contents do not directly mutate Ψ-Core state, grant authority, or activate governance.

## Boundary

### Gnozis-Core

- Ψ-state and relations
- candidate/test/verification/authorization/commit semantics
- protected invariants
- runtime execution boundaries
- canonical active state

### Gnozis Archive

- research records
- reverse-analysis records
- epochs
- snapshots
- summaries
- evidence references
- provenance
- rejected/failed/superseded historical material

The Archive preserves history; it does not become current truth merely because an item is stored there.

## Core invariants

1. Archive data is not Core authority.
2. Historical records remain distinguishable from current state.
3. Evidence status is not upgraded by copying or summarizing a claim.
4. Provenance must survive migration.
5. Raw evidence must not be silently replaced by summaries.
6. Export must be reproducible and idempotent.
7. Archive ingestion must not mutate Ψ-Core.
8. Core must remain operational without the Archive being available.

## Initial structure

archive/
- README.md
- SCHEMA_VERSION.md
- INDEX.yaml
- schema/record.schema.json
- records/README.md

This is the foundation only. Existing research material is not migrated until its provenance and schema mapping are defined.

## Status

Architecture foundation: IMPLEMENTED.
Record migration: NOT STARTED.
Automatic Core → Archive export: NOT IMPLEMENTED.
Archive → Core authority: NOT PERMITTED.