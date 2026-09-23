# Self-Optimization Evolution Contract

Status: THEORETICAL / branch contract
Branch: `evolution/self-optimization`
Base: `e9e56b610e10911d3a197a539df1840acbbd00ca`

## Purpose

Provide a separate evolution track for resource-aware self-optimization without weakening Ψ-Core integrity, trust boundaries, auditability, determinism, or governance.

The objective is not unrestricted self-modification. The objective is to make resource use an explicit constraint that the evolution system can observe, test, and optimize.

## Non-negotiable boundaries

- No self-optimization may mutate Ψ-Core invariants directly.
- No optimizer may bypass Candidate -> Test -> Verify -> Commit.
- Resource pressure must never silently disable security, verification, audit, provenance, or recovery checks.
- Optimization proposals are candidates, not authority.
- Performance measurements are evidence, not permission.
- Failed or ambiguous optimization experiments must fail closed and remain auditable.
- No global hidden clock or hidden resource state may influence Core semantics.
- Resource budgets are explicit inputs/constraints at the orchestration boundary.
- Production acceptance requires reproducible evidence and regression coverage.

## Resource model

Track at least:

- CPU time / execution budget
- memory high-water mark
- database I/O
- disk growth
- test/runtime duration
- repeated/redundant work
- concurrency/queue pressure where applicable

The first implementation should prefer coarse, deterministic counters and explicit budgets over platform-specific telemetry.

## Optimization loop

```
Observe resource cost
        ↓
Detect inefficiency
        ↓
Form Optimization Proposal
        ↓
Test / benchmark
        ↓
Verify correctness + integrity
        ↓
Shadow evaluation
        ↓
Governance
        ↓
Commit only if authorized
        ↓
Measure again
```

Optimization must therefore remain subordinate to the existing evolution trust graph.

## Required adversarial cases

1. Resource exhaustion.
2. Budget boundary / off-by-one.
3. Optimization that improves speed but changes semantics.
4. Optimization that reduces verification coverage.
5. Optimization that bypasses audit/provenance.
6. Optimization that increases memory/disk while reducing CPU.
7. Repeated optimization oscillation.
8. Measurement poisoning or stale baseline.
9. Concurrent optimization proposals targeting the same resource.
10. Recovery after an interrupted optimization experiment.

## Initial acceptance criteria

The branch is not production-ready until:

- resource limits are explicit;
- exceeding a budget is observable and deterministic at the relevant boundary;
- optimization cannot bypass existing trust-boundary checks;
- accepted optimization has before/after evidence;
- rollback/recovery is defined;
- audit/provenance records identify the optimization proposal and evidence;
- CI contains adversarial resource-budget tests;
- no optimization is allowed to silently trade security/integrity for performance.

## Relationship to self-learning

Self-optimization is a separate capability dimension:

```
Self-learning:
    discover / propose knowledge or rules

Self-optimization:
    discover / propose improvements to resource usage

Both:
    Candidate
      → Test
      → Verify
      → Shadow
      → Governance
      → Commit
```

Neither capability receives authority from its own measurement.

## Current status

This branch defines the contract only. No production optimization mechanism is enabled by this document.

Next task:

```
R2.OPT-1
Explicit Resource Budget + Measurement Boundary
```

Required before implementation:
- identify current orchestration boundaries;
- identify existing tests and CI limits;
- define resource measurements that do not alter Core semantics;
- add adversarial tests before enabling adaptive optimization.
