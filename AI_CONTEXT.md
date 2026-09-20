# Gnozis-V2 — AI Context

## 0. PURPOSE / OPERATING RULE

This file is the operational handoff for AI agents working on Gnozis-V2.

Repository:
- GitHub: Mikhail-Kucheriavyi-23/Gnozis-V2
- default branch: main

Rules:
1. Repository code, tests and actual runtime/CI evidence outrank chat memory or this document.
2. This document is architecture/research context, not proof of PASS.
3. Never claim a test, CI run, artifact, recovery result or security property was verified unless it was actually executed/inspected.
4. Select exactly one highest-priority READY task at a time.
5. Preserve rejected, failed, quarantined and insufficient-evidence outcomes as historical data.
6. Never weaken an invariant or evidence gate merely to make tests green.

## 1. ARCHITECTURAL PURPOSE

Gnozis-V2 is an autonomous recursive evolution research system whose canonical state/evolution semantics remain controlled by Ψ-Core.

Canonical evolution remains CLOSED until the complete evidence, sandbox, governance, security, quarantine and recovery chain is independently verified.

## 2. NON-NEGOTIABLE PRINCIPLES

- Ψ-Core is the authoritative source of state/evolution semantics.
- No second state model may silently diverge from Core.
- No AI model belongs inside Ψ-Core.
- External data is untrusted by default.
- External evidence may generate candidates/challenges but does not directly authorize Core mutation.
- Missing evidence remains UNKNOWN / INSUFFICIENT_EVIDENCE.
- Rejection is valid historical evidence.
- Persistence is evidence/provenance infrastructure, not an authority source.
- Hash-chain integrity is not semantic truth.
- A trigger is not authorization.
- Detection is not modification authority.
- A successful experiment is not canonical evolution.
- Mathematical closure is not runtime verification.

## 3. CORE EVOLUTION CHAIN

Candidate → Test → Verify → Authorize → Commit → ObserveOutcome → Recover/Verify

For architectural claims:

Claim → Invariant → Enforcement → Evidence → Scope

For reflection/evolution:

Findings → Counterexamples → RuleProposal → Shadow Evaluation → Governance

No PATCH or REDESIGN is authorized merely by mathematical analysis.

## 4. CURRENT RESEARCH STATUS

Formal/architectural research maturity remains approximately 96% as a working analytical estimate.
Runtime enforcement maturity remains substantially lower and must be reported separately.
These percentages are NOT software coverage measurements.

Previously verified persistence/reflection gates must not be reopened without concrete regression evidence.

## 5. HARD EPISTEMIC DISTINCTIONS

Preserve all of the following:

- Evidence ≠ Verification ≠ Authority.
- Identity ≠ Authority.
- Receipt ≠ Authorization.
- Persistence ≠ Canonical Authority.
- Hash-chain integrity ≠ Event Truth.
- TestPassed ≠ Complete Verification.
- Observation ≠ Representation ≠ Interpretation ≠ Claim.
- Integrity ≠ Adequacy ≠ Truth ≠ Reinterpretability.
- Internal consistency ≠ External correspondence.
- External evidence ≠ External control.
- Counterexample ≠ Exception.
- Explanation ≠ Causal proof.
- History ≠ Truth.
- Lineage proves descent, not legitimacy.

## 6. EPISTEMIC HISTORY / REALITY COUPLING

### E7.2.158 — History as Epistemic Anchor

Completed analytical result:

1. History can anchor provenance, lineage and historical hypothesis generation, but cannot establish truth by itself.
2. Cryptographic integrity proves that a recorded sequence is intact relative to its commitment structure; it does not prove that recorded events are semantically true.
3. Lineage proves descent/continuity, not legitimacy of the transition.
4. Immutable events may have revisable interpretations; interpretation changes must themselves be recorded as traceable historical events.
5. Historical evidence is evidence under an epistemic regime. If that regime is later found inadequate, prior records should be reclassified/reviewed rather than silently rewritten.
6. History can generate invariant candidates/hypotheses; observed historical regularity is not automatically normative necessity or a law.
7. Present governance must not retroactively manufacture or rewrite the historical evidence that supposedly justifies it.
8. Non-retroactive epistemic causality is a required boundary: past events constrain present reasoning; present decisions must not rewrite past events.

Key formulation:

History = Evidence Substrate, not Epistemic Oracle.

Historical anchor requirements, conceptually:

Tamper-evident + Traceable + Temporally ordered + Interpretation-versioned

This does NOT imply Truth.

### E7.2.159 — Reality Coupling

Completed analytical result:

1. A self-consistent internal history can still be completely wrong about the external world.
2. Internal consistency ≠ external correspondence.
3. For empirical claims, Gnozis requires a reality-coupling path through which information can enter that is not generated solely by the current internal model.
4. Reality coupling provides a possibility of correction, not an oracle of guaranteed truth.
5. External input must enter through an epistemic/evidence layer, not directly as canonical authority.
6. External sources may be wrong, correlated, stale or compromised; source count is not independence.
7. Epistemic openness requires not only external information but genuine exposure to potentially disconfirming evidence.
8. External evidence has epistemic authority about a claim only to the extent justified by its provenance/validation; it does not thereby obtain operational authority over Core.
9. Claim type matters: formal, empirical and mixed claims require different evidence structures.
10. Prediction and observation must remain distinguishable. Prediction error is a learning signal, not something that may be silently deleted.

Minimal conceptual reality-coupling structure:

ExternalObservation
  ↓
CandidateEvidence
  ↓
Verification / Validation
  ↓
Claim / Reflection
  ↓
Governance

ExternalObservation must NOT directly imply Core Commit.

Central formulation:

The system does not need an oracle of truth; it needs a persistent possibility of being wrong.

## 7. EXCEPTIONS / FALSIFIABILITY

### E7.2.160 — Exception Accumulation and Model Self-Immunity

Completed analytical result:

1. A counterexample is an observation conflicting with a model/claim; an exception is a hypothesis explaining why the conflict need not require model revision.
2. Exception classification is itself a claim and requires justification.
3. An exception must preserve a bounded scope. An exception that removes all predictive constraints is equivalent to abandoning the model.
4. Falsifiability must remain structurally non-empty after exceptions are introduced.
5. Exception severity depends on structural depth, not merely count.
6. Local anomalies may receive local investigation; repeated/structural contradictions should escalate toward model revision; core contradictions require revision pressure.
7. Exceptions must preserve the original contradiction as traceable evidence. Contradictions must not be deleted merely because an exception was accepted.
8. Exception drift must be prevented: the interpretation/scope of an exception may evolve, but its immutable origin must remain linked to the original counterexample.
9. If an exception acquires substantial predictive structure, it should be treated as a model-extension/revision candidate rather than a permanent ad-hoc exception.
10. Zero exceptions does not prove a strong model; a trivial/unconstrained model may simply avoid making falsifiable claims.
11. Successful explanations should themselves become candidates for adversarial testing.
12. A self-generated counterexample mechanism is not automatically complete; challenge diversity and evaluator independence remain separate concerns.

Conceptual escalation:

Counterexample
  ↓
ExceptionCandidate
  ↓
Justification
  ↓
Adversarial Challenge
  ↓
Accept / Reject / Revise

Repeated or structural contradiction:

Counterexamples → ModelRevisionCandidate

Central formulation:

Exceptions may protect a model locally, but must not make the model globally unfalsifiable.

And for the project's tension principle:

Tension must decrease through increased explanatory adequacy, not through deletion or semantic disappearance of the contradiction.

## 8. PROVENANCE MODEL

Evidence should remain a layered chain:

Observation
  ↓
Representation
  ↓
Transformation / Interpretation
  ↓
Claim

Context as applicable:
Assumptions + Dependencies + Loss + Schema/Version + Source/Time identity

For reality-linked claims, additionally preserve the source/observation path and validation context.

Immutable event + revisable interpretation is preferred to mutable historical rewriting.

## 9. GOVERNANCE / AUTHORITY BOUNDARY

Governance is classification and evidence evaluation, not an unrestricted autonomous authority source.

Critical rule:

Detection ≠ Modification Authority.

A finding that a rule is inadequate does not itself authorize removal of that rule.

Similarly:

External Challenge ≠ External Command.

The external world may provide evidence/counterexamples, but external inputs must not bypass internal verification and protected Core invariants.

For evolving evidence standards:

A rule change that increases authority must not be justified solely by the rule being changed or by evidence generated entirely under the assumptions that the change itself is attempting to weaken.

No self-justified authority growth.

## 10. VERIFICATION BOUNDARY

Verifier evolution is distinct from system evolution.

Critical verification boundaries must preserve detection capability by default. A verifier may evolve only through explicit, evidence-backed governance; the mechanism being verified must not be the sole authority for redefining the critical boundary by which it is verified.

Verification provenance should retain, as applicable:
Claim, Scope, SystemID, VerifierID, OracleID, EnvironmentID, Result, EvidenceProvenance, SemanticsVersion.

Differential verification, adversarial verification and multiple evidence paths are useful only when their dependency/common-mode structure is understood.

## 11. RESEARCH CHAIN — COMPLETED RECENT LAYERS

E7.2.44 — minimal verification basis/test-set sufficiency.
E7.2.45 — verifier evolution/oracle drift/self-reference.
E7.2.46 — observability/measurement invariance/cross-version comparability.
E7.2.47 — causal attribution of verification changes.
E7.2.115 — experiment design under foundational uncertainty.
E7.2.116 — interpretation independence.
E7.2.117 — minimal epistemic representation.
E7.2.158 — history as epistemic anchor.
E7.2.159 — reality coupling.
E7.2.160 — exception accumulation / falsifiability / model self-immunity.

Intermediate E7.2 layers between these checkpoints remain part of the ongoing reverse-analysis record from prior context and should not be treated as implementation verification.

## 12. CURRENT NEXT REVERSE-ANALYSIS TARGET

### E7.2.161 — Adversarial Completeness and Ontology Lock-In

Key questions:

- Who/what controls the space of possible counterexamples?
- Can a self-evolving system discover contradictions that its own ontology cannot represent?
- How can counterexample generation avoid becoming a closed confirmation mechanism?
- What forms of evaluator/challenge diversity are actually independent?
- What is the minimal representation needed to detect an error outside the current model's categories?
- When does a missing category itself become evidence of ontology failure?

Method:

Counterexample Space
  ↓
Representation Boundary
  ↓
Blind-Spot Analysis
  ↓
Independent Challenge Generation
  ↓
Ontology Expansion Candidate
  ↓
Adversarial Verification
  ↓
Governed Rule/Model Proposal

Status: RESEARCH ONLY; no implementation authorization.

## 13. IMPLEMENTATION SAFETY

Do not convert any of E7.2.158–E7.2.160 directly into code without a bounded architecture review and executable acceptance criteria.

Do not:
- create speculative Genesis/meta-evolution APIs;
- allow external inputs to bypass evidence gates;
- turn exceptions into silent truth overrides;
- delete counterexamples from history;
- claim falsifiability merely because tests exist;
- claim reality correspondence from internal consistency or hash-chain integrity;
- reopen verified persistence gates without regression evidence.

## 14. COMPLETION EVIDENCE FORMAT

For every completed implementation task record:

Task ID:
Status:
Implementation:
Files changed:
Tests added/changed:
Tests actually executed:
Observed result:
CI run / commit:
Known limitations:
New dependencies discovered:
Adversarial checks:
Next task:

Never write “verified” without evidence.

## 15. FINAL SELF-EVOLUTION RULE

Canonical self-evolution remains CLOSED.

Required chain before canonical mutation:

Candidate
 ↓ Generate
 ↓ Test
 ↓ Sandbox execution
 ↓ observed evidence
 ↓ Shadow evaluation
 ↓ Invariant delta
 ↓ Governance/evidence gate
 ↓ PromotionCandidate
 ↓ security/quarantine/recovery gates
 ↓ ONLY THEN canonical mutation

A promotion candidate is not a Core mutation.
A passing unit test is not complete architectural verification.
CI-green must be tied to an exact commit/run.

## 16. HANDOFF

Current research handoff:
- E7.2.160 completed analytically.
- No implementation authorization follows from E7.2.158–E7.2.160.
- Next target: E7.2.161 Adversarial Completeness and Ontology Lock-In.
- Repository code/tests/CI remain authoritative over this research document.
