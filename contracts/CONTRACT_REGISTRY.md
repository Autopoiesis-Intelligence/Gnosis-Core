# Gnozis Contract Registry

Version: 2026-09-23.1
Repository: Gnozis-V2
Branch baseline: main
Purpose: machine-readable control layer for one-shot and recurring project contracts.

## Contract classes

- ONE_SHOT: finite acceptance conditions; closes as DONE, REJECTED or BLOCKED.
- RECURRING: permanent control feature; each execution produces evidence and a new run record.
- RESEARCH: analytical contract; may remain HYPOTHESIS/OPEN and does not authorize implementation.
- VERIFICATION: evidence-generation contract; PASS is valid only when the stated evidence was actually produced.

## Current active one-shot frontier

### R2 adversarial runtime / trust-boundary reverse-analysis
Status: ACTIVE
Priority: P0
Current target: continue the numbered R2 sequence from the latest accepted node.
Rule: do not convert documentation into runtime evidence.

### Fixed-point semantics correction
Status: OPEN
Priority: P0
Requirement:
  Valid(Ψ) ∧ Ψ'=Ψ => viable(Ψ,Ψ)=True
while changed dead-end candidates remain rejectable.
Acceptance requires source change plus real tests/CI evidence.

### Fresh full regression
Status: OPEN
Priority: P0
Acceptance requires an actual execution against the exact resulting commit. Historical CI or test files are not sufficient.

### RM-CORE-R1 — Research Machine / Core Boundary
Status: ACTIVE
Priority: P0
Purpose: controlled separation of research material from canonical Core while preserving provenance and the Knowledge Interface.

## Recurring contracts

1. RECUR-MATH-001 — Mathematical Reference Synchronization
2. RECUR-MATH-002 — Mathematics ↔ Architecture Reconciliation
3. RECUR-MATH-003 — Mathematical Sandbox Conformance
4. RECUR-MATH-004 — Mathematical Drift Detection
5. RECUR-MATH-005 — Proof / Counterexample Maintenance
6. RECUR-MATH-006 — Architecture Description Synchronization
7. RECUR-CONTRACT-001 — Contract Registry Synchronization
8. RECUR-EVIDENCE-001 — Runtime/CI Evidence Freshness
9. RECUR-R2-001 — Adversarial Mutation/Trust-Boundary Sweep

## Control rule

Recurring contracts never increase or decrease the finite one-shot completion denominator. They have their own health state:

ACTIVE | HEALTHY | DEGRADED | BLOCKED | NEEDS_REVIEW

A recurring execution may create one-shot tasks when it discovers a concrete gap.

## Authority rule

This registry is a control description, not proof. Repository source, reproducible runtime behavior and real CI evidence outrank registry claims.
