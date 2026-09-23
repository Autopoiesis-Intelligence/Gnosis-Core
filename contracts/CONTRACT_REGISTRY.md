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

## Newly confirmed evidence requiring follow-up

### Evolution memory semantic tamper
STATUS: OPEN
EVIDENCE: CI run 1180, Python 3.11, exact tested predecessor commit 8d3681a…
FINDING: tests/test_evolution_memory.py::test_load_evolution_memory_rejects_transition_semantic_tamper[to_state_id] did not raise StorageCorruptionError.
IMPLICATION: persistence semantic-integrity boundary is not fully verified.
NEXT: bounded corrective task after the current active task gate permits.

### Recovery duplicate provenance links
STATUS: OPEN
EVIDENCE: CI run 1180, Python 3.11, exact tested predecessor commit 8d3681a…
FINDING: tests/test_evolution_recovery.py::test_recovery_fails_closed_on_duplicate_provenance_audit_links raised IndexError: tuple index out of range.
IMPLICATION: recovery fail-closed behavior has a concrete defect under the tested adversarial case.
NEXT: bounded corrective task after the current active task gate permits.

### Dependency Review workflow
STATUS: BLOCKED / REPOSITORY CONFIGURATION
EVIDENCE: GitHub Dependency Review run 4.
FINDING: GitHub reports Dependency Review unsupported because Dependency graph is not enabled.
IMPLICATION: workflow cannot currently provide its intended evidence.
NEXT: repository-security configuration task; do not misclassify as a code dependency vulnerability.


## 2026-09-23 P0 priority update

P0 evidence gate has been instantiated as Issue #13.

Priority order:
1. P0 persistence/recovery semantic-integrity failures from CI.
2. P0 fixed-point semantics correction.
3. P0 fresh full regression on the exact resulting commit.
4. P0 R2 adversarial trust-boundary continuation.
5. P0 RM-CORE-R1 Research Machine/Core boundary.
6. Recurring mathematical reconciliation and exhaustive mathematical reconstruction continue in parallel where they do not mutate Core.

No lower-priority task may be used to bypass an unresolved P0 runtime failure.
