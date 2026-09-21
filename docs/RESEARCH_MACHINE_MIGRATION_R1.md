# Gnozis Research Machine — First Migration Record

## Source

Original source path: `diagnostic_corpus/SELF-DIAGNOSTIC-0001/`

Source status: controlled experimental evidence.

Source generation program: `diagnostic_corpus/generate.py`

## Classification

Research Machine candidate: **YES**

Reason: the corpus is a reproducible controlled experiment used as evidence for reflection experiments. It is not canonical production history and its own verification gate requires real runtime evidence before verification.

## Preservation rule

The first migration must preserve the original artifact semantics and provenance. It must not convert `UNVERIFIED` into `VERIFIED`, and it must not turn expected experiment properties into findings about Core.

## Evidence envelope

- artifact_id: `SELF-DIAGNOSTIC-0001`
- scenario: `controlled-persisted-runtime-history`
- transition_count: 4
- rejected_count: 3
- accepted_count: 1
- test_rule_id: `test-rule:diagnostic-policy`
- persistence: `sqlite_round_trip`
- source verification gate: `UNVERIFIED`

## Migration decision

Do not physically move the corpus yet.

First create the Research Machine record contract and verify that the source artifact can be represented without semantic loss. The current corpus remains in V2 until that contract is validated.

## Why this is the first candidate

This corpus has unusually clear boundaries:

`Core execution → persistence → recovery → self-diagnostic → diagnostic artifact`

It already carries scenario and generation provenance, and its verification file explicitly distinguishes executable evidence from claims.

## Next

1. Define a record mapping.
2. Validate source hashes / baseline.
3. Create a machine-readable Research Machine record.
4. Only then perform physical extraction.


## Reconciliation with the existing Research Machine

The repository inventory revealed that the former Gnozis repository already contains a mature machine-readable research/evidence layer under its legacy archive/ path. That layer is semantically the **Gnozis Research Machine**: it has canonical record IDs, typed records (R/C/E/X/D/A/T), provenance, relations, evidence references, engineering consequences, admissibility states, and an explicit non-authoritative Core boundary.

Therefore Gnozis-V2 must not invent a competing Archive schema or maintain a second historical-memory system.

The temporary archive/ foundation previously created in V2 has been removed. The canonical Research Machine schema remains the existing schema in the research repository until the physical directory rename to research_machine/ is performed as a controlled repository-level migration.

### Consequence for SELF-DIAGNOSTIC-0001

The diagnostic corpus remains in V2 for now. Its expected-properties and verification gate are source material for a future Research Machine record, but the absence of generated runtime artifacts means the source does not yet contain a completed diagnostic result to migrate as verified evidence.

The first migration therefore requires a record mapping against the **existing Research Machine v1 schema**, not the temporary V2 schema.

### New rule

There must be exactly one canonical Research Machine knowledge/evidence model for the project. Gnozis-V2 may contain operational references and bounded experiment generators, but it must not create a second archive/history ontology.
