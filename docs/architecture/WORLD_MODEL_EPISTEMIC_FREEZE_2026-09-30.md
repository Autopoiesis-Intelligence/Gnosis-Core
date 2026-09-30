# World Model / Epistemic Architecture Freeze

Date: 2026-09-30
Status: THEORY FREEZE — implementation not yet authorized by this document

## Scope

This record freezes the theoretical result of the World Model / Epistemic audit before repository implementation.

## 1. Boundary

World Model and Core Evolution are separate semantic domains.

World Model:
- WorldObservation
- Representation
- Measurement
- Relation
- Evidence
- Provenance
- EpistemicTransition
- Tension
- EpistemicState

Bridge:
- Finding

Core Evolution:
- Candidate
- Test
- Select
- Verify
- Governance
- Authorization
- Commit

No World Model primitive may directly mutate canonical Core State, create authorization, or commit a Core change.

## 2. Non-duplication

Reuse existing infrastructure where semantically compatible:
- Relation
- Evidence
- Provenance
- Context / Scope
- canonical digest / identity
- normalization
- Finding
- Candidate
- existing persistence / replay / audit mechanisms

Do not introduce parallel WorldEvidence, WorldRelation, WorldContext, WorldDigest, WorldNormalization, or WorldCandidate systems without a demonstrated contract gap.

## 3. Epistemic rules

- Observation is not truth.
- Evidence is not truth.
- Provenance is not authority.
- Hash integrity is not semantic truth.
- Representation disagreement is not automatically world contradiction.
- Tension is a detected unresolved relation, not a truth declaration.
- Newer evidence does not automatically win.
- Tension resolution requires explicit evidence/verification.
- Historical records are immutable; supersession is represented by new records/transitions.

## 4. Identity and persistence

New immutable primitives use canonical content identity.

Identity must be recomputable after reload and compared with the stored identity.

Persistence must not be authority.

Timestamp is metadata, not semantic identity.

Epistemic status changes are append-only transition records, not in-place mutation.

Replay must reconstruct the same epistemic state deterministically.

## 5. Proposed minimal new primitives

- WorldObservation
- Representation
- Measurement
- EpistemicTransition
- Tension

Existing Relation remains reusable unless implementation proves a semantic gap.

## 6. Runtime model

A three-speed execution model (fast ingestion, medium projection/indexing, slow epistemic processing) is an engineering hypothesis/benchmark target, not yet an implementation fact.

Claims such as microsecond latency or hundreds of thousands of observations/sec require benchmark evidence and must not be recorded as verified architecture properties.

## 7. Evolution loop

Observe
→ Epistemic evaluation
→ Finding
→ Candidate
→ Test
→ Verify
→ Governance
→ Authorization
→ Commit
→ Observe consequence

A Commit is not evidence of successful external effect. Consequences return through Observation/Evidence.

## 8. Required implementation order

R1 Domain types
R2 Canonical identity
R3 Durable persistence + reload/tamper tests
R4 Epistemic transitions + Tension
R5 Finding adapter
R6 Replay
R7 Adversarial CI
R8 Performance benchmarks

Correctness precedes optimization.

## 9. Explicitly out of scope for R1

- new database engine
- new Evidence Ledger
- new authorization system
- automatic truth acceptance
- automatic Tension resolution
- direct World → Commit path
- production performance claims without benchmarks
- autonomous redesign of Ψ-Core

## 10. Architectural gate

The first repository implementation must preserve:
- Ψ-Core as canonical state/evolution authority
- protected commit semantics
- immutable historical records
- provenance/evidence separation
- no hidden selector
- no authority leak from storage, observation, evidence, or detection

This document freezes theory only. It does not by itself establish runtime verification of any new primitive.
