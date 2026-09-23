# Recurring Contracts

These are permanent project features, not tasks that become permanently DONE.

## RECUR-MATH-001 — Mathematical Reference Synchronization

Objective:
Maintain the canonical mathematical model reconstructed from project research.

Sources:
- research conversations and mathematical derivations;
- accepted counterexamples;
- formal definitions and proofs;
- architectural findings.

Output:
A versioned mathematical snapshot with provenance and status.

## RECUR-MATH-002 — Mathematics ↔ Architecture Reconciliation

For each mathematical object m:
  Coverage(m,A) ∈ {MATCH, PARTIAL, GAP, UNPROVEN, OUT_OF_SCOPE}

For each architectural mechanism a:
  Basis(a,M) ∈ {DERIVED, SUPPORTED, UNJUSTIFIED, UNKNOWN}

The reconciliation must run after material mathematical or architectural changes.

## RECUR-MATH-003 — Mathematical Sandbox Conformance

For a formal obligation C:
  Runtime(A,C) |= M(C)

Failure produces a finding. It does not directly mutate Core.

The sandbox is evidence infrastructure, not canonical authority.

## RECUR-MATH-004 — Mathematical Drift Detection

Track separately:
  ΔM = change in mathematical reference
  ΔA = change in architecture
  Drift(M,A) = semantic mismatch requiring investigation

Documentation changes alone cannot close a drift finding.

## RECUR-MATH-005 — Proof / Counterexample Maintenance

Every new proof is checked against existing counterexamples.
Every new counterexample records which claim it:
  REFUTES | REFINES | RESTRICTS | EXTENDS | DOES_NOT_AFFECT

Contradicted mathematics remains historical evidence.

## RECUR-MATH-006 — Architecture Description Synchronization

Current mathematical and architectural state is reconciled before project descriptions are updated.

Direction:
  Mathematics → Architecture State → Public/AI Description

The description never becomes the source of truth.

## RECUR-CONTRACT-001 — Contract Registry Synchronization

Maintain one machine-readable registry for finite and recurring contracts, with explicit dependencies, evidence and acceptance conditions.

## RECUR-EVIDENCE-001 — Runtime/CI Evidence Freshness

No IMPLEMENTED/PASS claim is refreshed merely because code or documentation exists. The exact commit and actual execution evidence must be recorded.

## RECUR-R2-001 — Adversarial Mutation/Trust-Boundary Sweep

Re-scan all canonical mutation classes:
Evolution, Reflection, Execution, Storage, Recovery, Fork/Clone, Delegation, Capability activation, protected policy/verifier updates, external bridge, replay/rollback, concurrency/stale authorization.

For each:
Entry → Validation → Authorization → PowerImpact → Commit → Audit → Persistence/Activation.

## Recurring run record

Each execution should produce:
RUN-ID
DATE
BASE-COMMIT
SCOPE
OBSERVATIONS
FINDINGS
NEW_TASKS
EVIDENCE
STATUS
NEXT

A recurring contract is healthy only when its last run is traceable to an exact project state.
