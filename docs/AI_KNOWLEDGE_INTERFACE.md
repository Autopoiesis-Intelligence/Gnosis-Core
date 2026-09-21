# Gnozis Core — Research Knowledge Interface

## Purpose

The Research Library is the durable, machine-readable knowledge layer for Gnozis. Gnozis Core remains the minimal execution and verification layer.

The Core may consume research-derived records through an explicit interface. Research material does not acquire authority merely by being present in the library.

## Separation

Research Library:
- discoveries;
- reverse-analysis;
- formal models;
- findings;
- counterexamples;
- research decisions;
- engineering consequences;
- provenance.

Core:
- canonical state;
- transitions;
- invariants;
- verification;
- persistence;
- provenance enforcement;
- governance.

## Admission path

Observation → Pattern → Formalization → Evidence → Engineering Consequence → Core Requirement → Bounded Task → Implementation → Test/CI → Audit → Acceptance.

A research record without an engineering consequence remains research.

## Machine-readable record

Each admitted research unit should expose, at minimum:

```yaml
id:
type:
parent:
question:
observation:
derivation:
result:
evidence:
engineering:
  consequence:
  gap:
core:
  admissibility:
  affected_area:
status:
next:
```

The human-readable research document and machine-readable record must reference the same stable identifier.

## Authority rule

Research can inform Core; it cannot directly mutate or authorize Core.

Core must validate applicability, preserve invariants and require the normal evidence/acceptance path.

## Continuity

Conversation history is non-canonical. Continuity is reconstructed from stable research IDs, engineering task IDs, source commits, tests, CI evidence and audit records.

## Compact session reporting

Every substantive engineering/research session should end with:

```
[PROGRESS]
Research: <current node/range>
Engineering: <active task>
Core: <active phase>
Done: <completed work>
Evidence: <new evidence / pending>
Next: <single next action>
```

Percentages are used only when their denominator is explicit and reproducible.

## Core cleanliness rule

Research context must not be copied wholesale into Core. Core receives only the minimum structured information required by its bounded engineering interface.
