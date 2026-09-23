# GNOZIS EVOLUTION CONTRACT — UNIVERSAL TRIGGER

Trigger phrase:

**GNOZIS EVOLUTION CONTINUE**

Purpose: restore and continue the repository evolution workflow from any new chat.

## Operating mode

When this trigger is invoked, treat the repository as the source of truth. Inspect current code, tests, exact commit/branch state and CI evidence before making substantive claims or edits.

The assistant autonomously selects the next evolution contract. The user does not need to specify the next technical step.

Selection priority:
1. trust-boundary defect or unverified critical path;
2. adversarial verification gap;
3. dependency/blocking contract;
4. evidence/provenance gap;
5. only then new capability.

Never continue a lower-priority contract merely because it was previously started.

## Contract model

Evolution is divided into contracts. Each contract has:
- CONTRACT-ID
- STATUS
- PRIORITY
- DEPENDS_ON
- OBJECTIVE
- SCOPE
- DO_NOT_CHANGE
- REQUIRED EVIDENCE
- ADVERSARIAL TESTS
- ACCEPTANCE
- NEXT

Percentages represent completion of explicit acceptance/evidence blocks, not subjective quality scores.

Required status vocabulary:
- IMPLEMENTED
- PARTIAL
- MISSING
- THEORETICAL
- BLOCKED

Implementation is never treated as verification.

## Three independent statistics

Always report separately:

1. **Implementation** — what exists in the repository.
2. **Evidence** — what is actually supported by tests/CI/adversarial verification.
3. **Evolution Readiness** — what can safely participate in further autonomous evolution.

Do not collapse these into one number unless a canonical denominator exists.

## Evidence rules

- Code is evidence of implementation, not correctness.
- Documentation is not enforcement.
- Tests are not proof of adequacy by themselves.
- CI claims must be tied to an exact commit SHA.
- If CI is unavailable/incomplete, state that explicitly.
- Never invent test results, repository state, commits, links, or completed work.
- A green CI does not by itself establish trust-boundary integrity.
- Preserve provenance and auditability through every evolution stage.
- Fail closed where evidence is missing or ambiguous.

## Universal evolution loop

```
Observe
  → Evidence
  → Counterexample / Gap
  → Proposal
  → Candidate
  → Test
  → Verify
  → Shadow
  → Governance
  → Commit
  → Observe again
```

Resolve, Propose, Verify, Govern and Commit are distinct authorities/stages.

No self-learning or self-optimization mechanism may bypass this loop.

## Self-learning contract

Self-learning may discover/propose knowledge, rules, relations or improvements.

Current conceptual path:

```
Counterexample
→ RuleProposal
→ Shadow Evaluation
→ Governance
→ Commit
```

A proposal does not become authority merely because it was generated or performed well in shadow evaluation.

## Self-optimization contract

Self-optimization is a separate capability dimension inside the same evolution trust machinery.

Current path:

```
Resource Observation
→ Inefficiency / Redundancy Evidence
→ Optimization Candidate
→ Test
→ Verify
→ Shadow
→ Governance
→ Commit
```

Current directory branch:
`evolution/self-optimization`

Current work includes bounded resource measurement, directory observation, duplicate-content detection, and usage/protection/provenance gating for optimization candidates.

Non-negotiable:
- no direct mutation of Ψ-Core invariants;
- no bypass of verification/audit/provenance/recovery;
- resource pressure cannot silently disable security or verification;
- measurement is evidence, not permission;
- duplicate content is not automatically removable;
- directory optimization begins read-only;
- missing provenance blocks safe optimization candidacy;
- optimization cannot silently trade integrity/security for performance.

## Resource model

Track where relevant:
- execution time;
- CPU/execution budget;
- memory high-water mark;
- database I/O;
- disk growth;
- redundant work;
- concurrency/queue pressure.

Prefer explicit bounded measurements over hidden global telemetry.

## Directory optimization safety

```
Directory
→ Observation
→ Content Identity
→ Duplicate Relation
→ Usage
→ Protection
→ Provenance
→ Candidate Binding
→ Shadow
→ Governance
→ Commit
```

Never infer “safe to delete” from duplication alone.

## Required report after every pass

```
EVOLUTION REPORT
Active Contract: <ID>
Contract Progress: <percent>

Implementation: <percent>
Evidence: <percent>
Evolution Readiness: <percent>

Trust Boundary: <percent/status>
Self-Learning: <percent/status>
Self-Optimization: <percent/status>
Adversarial Coverage: <percent/status>

HEAD: <exact SHA>
Branch: <branch>
CI: <exact status tied to SHA>

Completed:
<short list>

Detected gaps:
<short list>

Next Contract:
<ID + objective>

Blockers:
<short list or NONE>
```

Keep the report concise but never omit it.

## Decision authority

The assistant chooses the next contract and may make repository changes when the required repository facts are available.

However:
- no claim of autonomous authority is inferred from this document;
- no generated proposal grants itself authority;
- trusted issuer / governance requirements remain explicit;
- repository changes remain subject to the project's existing trust and governance boundaries.

## Context restoration

On trigger invocation:
1. inspect current repository state;
2. inspect current branch/HEAD;
3. inspect relevant AI_CONTEXT/status/audit files;
4. inspect CI for the exact relevant SHA;
5. reconcile the last known contract state with actual repository evidence;
6. select the highest-priority safe next contract;
7. execute only the necessary bounded step;
8. verify;
9. update project state if appropriate;
10. emit the mandatory EVOLUTION REPORT.

This contract is itself a workflow trigger, not proof that any listed capability is implemented.


## Continuity rule — repository work never stalls

The evolution process is continuous.

When a safe repository change is available, implement the smallest bounded change and verify it. Do not wait for a later conversation merely because another check is pending.

If repository modification is not currently justified, blocked, or would weaken evidence, continue the evolution process by recording important deductions, hypotheses, contracts, gaps, or relations in the machine-readable research repository:
`Mikhail-Kucheriavyi-23/Gnozis/research_machine/`

Such records must be explicitly classified (for example `RESEARCH_ONLY`, `HYPOTHESIS`, `OPEN`, `OBSERVED`) and must not be represented as implemented capability.

## Autonomous contract selection

The assistant is responsible for selecting the next contract after inspecting current repository evidence.

The active self-optimization sequence currently includes:

- R2.OPT-1 Resource Boundary
- R2.OPT-2 Resource Exhaustion Semantics
- R2.OPT-3 Directory Redundancy Detection
- R2.OPT-4 Usage/Protection/Provenance Gate
- R2.OPT-5 Candidate Integrity
- R2.OPT-6 Evidence Binding
- R2.OPT-7 Provenance/Audit Closure
- R2.OPT-8 Shadow Optimization
- R2.OPT-9 Governance
- R2.OPT-10 Governed Commit

The sequence is not a rigid queue. A higher-priority trust, evidence, adversarial, CI, provenance, recovery, or security gap can interrupt and supersede a lower-priority contract.

## No artificial completion

Never increase a contract percentage because code was written alone.

Completion requires its explicit acceptance/evidence conditions.

If CI is pending, partial, unavailable, or tied to an older SHA, report that exact state.

## Research-machine continuity

Important conclusions from the evolution process should be persisted to the machine-readable research repository when they have value beyond a single implementation step.

A research record should preserve:
- unique record ID;
- statement;
- status;
- source commit(s);
- relations/provenance;
- engineering consequence;
- unresolved gap;
- core admissibility.

Research records do not grant implementation authority.

## Required continuity trigger

The phrase:

**GNOZIS EVOLUTION CONTINUE**

means:

```
restore contract state
→ inspect repository reality
→ reconcile evidence
→ select highest-priority contract
→ implement or research-record the next safe step
→ verify
→ report
→ continue
```

The trigger is valid in a new chat without requiring the user to reconstruct the previous conversation.
