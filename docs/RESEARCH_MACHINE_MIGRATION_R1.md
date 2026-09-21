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
