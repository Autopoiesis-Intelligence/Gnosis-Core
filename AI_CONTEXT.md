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

The E7.2 reverse-analysis branch has now reached a near-freeze point. E7.2.161–E7.2.170 produced a coherent candidate architecture boundary, but this is still analytical and is not implementation authorization.

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
- Repeated detection ≠ Independent evidence.
- Representation disagreement ≠ World contradiction.
- Representation agreement ≠ Truth.
- Selector ≠ Sovereign authority.
- Evaluation ≠ Absolute correctness.
- Low observed failure ≠ Adequate testing.

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

## 11. RESEARCH CHAIN — NEW COMPLETED ANALYTICAL LAYERS

### E7.2.161 — Adversarial Completeness and Ontology Lock-In

The counterexample space is itself bounded by representation. A self-evolving system can therefore fail to generate a contradiction that its ontology cannot express.

Key result:
- Missing category can itself become ontology-pressure evidence.
- Counterexample generation must not be treated as complete merely because it is internally self-generated.
- Challenge diversity and evaluator independence remain separate dimensions.
- A representation boundary is an epistemic boundary.
- Ontology expansion must remain a Candidate, not an automatic mutation.

### E7.2.162–E7.2.166 — Structural Tension, Pre-Semantic Detection and Boundary Instrumentation

Completed analytical synthesis:

1. Semantic contradiction requires a pre-existing semantic frame.
2. Structural tension can exist before the current ontology can name the conflict.
3. Therefore:
   StructuralTension ≠ SemanticContradiction.
4. A detector should initially emit CandidateTension rather than ContradictionTruth.
5. Structural tension may arise from prediction mismatch, transition mismatch, constraint incompatibility, recurrence anomalies, cross-domain structural recurrence, or model/behavior inconsistency.
6. Repeated detection is not equivalent to independent confirmation.
7. Detection should maximize anomaly visibility rather than explanatory certainty.
8. A detector's correctness does not establish detection adequacy; blind spots and meta-tests remain necessary.
9. Conflict should first become measurable before being forced into a semantic resolution.
10. The project principle “conflict is information and evolutionary rule” can be operationalized as:
    Tension → Boundary Representation → Tool Candidate → New Evidence → Possible Distinction.

Central formulation:

Detect tension without prematurely declaring contradiction.

### E7.2.167 — Pre-Semantic / Structural Tension Layer

A potential ontology-independent detection layer is conceptually required.

It should report:
- what does not fit;
- under which conditions;
- with what provenance;
- with what scope/limitations.

It should NOT directly assert:
- truth;
- causal explanation;
- ontology revision;
- Core mutation.

### E7.2.168 — Representation as Epistemic Hypothesis

Completed analytical result:

1. Representation is not a neutral container; it determines which distinctions are visible.
2. Therefore representation itself is an epistemic hypothesis.
3. Multiple representations may be needed under ontological uncertainty.
4. Representation disagreement is a potential epistemic signal, not automatic world contradiction.
5. A meta-representation can describe relations between representations, but unbounded meta-regression must be avoided.
6. A representation should be selected as a test instrument for a bounded question, not treated as a final truth container.
7. Each representation should expose provenance and epistemic limitations, including relevant information loss.
8. Representation has an observation boundary:
   R: W → O_R
   where W \ O_R is information not distinguished by R.
9. Representation differential can reveal hidden distinctions:
   R1(A)=R1(B) while R2(A)≠R2(B)
   indicates representation-dependent equivalence, not immediate objective truth.
10. Ontology pressure is evidence that a current distinction/equivalence may be representation-dependent; it is not itself proof of a new ontology.

Conceptual Representation Contract:

{source, method, assumptions, scope, loss, dependencies, provenance}

### E7.2.169 — Adaptive Representation Selection

Completed analytical result:

1. There is no absolute BestRepresentation.
2. Representation utility is conditional on the current tension, hypothesis space and budget.
3. Selection should support both discrimination and discovery.
4. Closed hypothesis spaces can create closed evolution; discovery must sometimes search outside the current hypothesis categories.
5. Exploration and exploitation are resource-allocation modes, not Core truths.
6. Selection must account for epistemic independence, not merely syntactic diversity.
7. Different outputs do not imply independent evidence.
8. Representation families can share common-mode failure; family escape is therefore a legitimate experimental objective.
9. Selection criteria should remain multi-objective; a single total score can hide tradeoffs.
10. A selector may exist above Core, but it must not silently redefine Core transition semantics or directly mutate Ψ.
11. Selection provenance is part of epistemic audit.
12. The selector is an experimental policy, not a sovereign authority.

Conceptual chain:

Tension
  ↓
CandidateRepresentations
  ↓
Selection
  ↓
Experiment
  ↓
Evidence
  ↓
Interpretation
  ↓
Candidate
  ↓
Verification
  ↓
Commit

### E7.2.170 — Bounded Self-Evaluation

Completed analytical result:

1. An ultimate evaluator is not required.
2. Self-evaluation should verify bounded, explicit properties rather than claim absolute correctness.
3. Immutable Core constraints must bound mutable experimental policy.
4. Selector evaluation may inspect budget compliance, provenance, diversity, dependency structure, challenge coverage and behavioral failure patterns.
5. Selection history is required to detect concentration, bias and epistemic stagnation.
6. Low observed failure is ambiguous: it may indicate robustness or weak testing.
7. Evaluation results are evidence about properties, not unconditional verdicts.
8. Reflection may generate findings/counterexamples/rule proposals about selector behavior, reusing the existing reflection/governance pattern where appropriate.
9. Reflection or self-evaluation may propose policy changes but must not unilaterally authorize them.
10. Meta-evaluation should terminate in bounded uncertainty, not recurse toward absolute certainty.
11. A protected set of Core invariants + observable history + independent challenge mechanisms provides a bounded self-evaluation architecture.

Key formulation:

Selector is not sovereign.

Evaluation is not absolute correctness.

Meta-evaluation may establish bounded properties and limitations, not perfection.

## 12. CURRENT ARCHITECTURAL IMPLICATION — NOT YET IMPLEMENTATION AUTHORIZATION

E7.2.161–E7.2.170 collectively indicate a likely architecture boundary:

Ψ-Core should remain the protected semantic/state-transition authority.

A higher epistemic/experimental layer may be required around Core for:
- structural tension registration/detection;
- representation candidates and provenance;
- adaptive experiment selection;
- experiment execution;
- evidence capture;
- historical revisit;
- selector/reflection analysis.

However, this does NOT yet authorize creation of new modules.

Before implementation, perform an Architecture Delta review against existing:
- reflection;
- verification;
- storage;
- governance;
- audit/provenance;
- existing execution-authorization boundaries.

Prefer reuse over parallel subsystems.

Potential conceptual flow:

StructuralTension
  ↓
RepresentationCandidates
  ↓
ExperimentalSelection
  ↓
Experiment
  ↓
Evidence
  ↓
Reflection / Interpretation
  ↓
Candidate
  ↓
Core Verification
  ↓
Governance
  ↓
PromotionCandidate
  ↓
Protected Commit

The selector may choose experiments but must not directly authorize canonical Core mutation.

## 13. CURRENT REVERSE-ANALYSIS REPORT

Working estimates only; NOT test coverage:

- Overall project analytical progress: approximately 74% (rough working estimate; keep separate from software/runtime maturity).
- E7.2 branch: approximately 95% complete as of E7.2.170.
- Architecture understanding for the current branch: approximately 90%+.
- Runtime enforcement of the newly derived mechanisms: not established by this research sequence.
- Architecture Delta is now near-ready, but Reverse Freeze has not yet been declared.

Next analytical step:

### E7.2.171 — E7.2 Synthesis / Architecture Delta Review

Objective:
- consolidate E7.2.161–E7.2.170;
- distinguish what is genuinely new from what existing Gnozis-V2 already covers;
- identify the minimum architecture delta;
- explicitly list what must NOT be changed;
- map requirements to existing modules before proposing new modules;
- define executable acceptance criteria only after the delta is understood.

No implementation should start merely because E7.2.170 is complete.

## 14. IMPLEMENTATION SAFETY

Do not convert E7.2.161–E7.2.170 directly into code without a bounded architecture review and executable acceptance criteria.

Do not:
- create speculative Genesis/meta-evolution APIs;
- allow external inputs to bypass evidence gates;
- turn exceptions into silent truth overrides;
- delete counterexamples from history;
- claim falsifiability merely because tests exist;
- claim reality correspondence from internal consistency or hash-chain integrity;
- treat representation disagreement as proof of world contradiction;
- treat selector output as canonical authority;
- create a parallel governance system if existing reflection/governance can be reused;
- reopen verified persistence gates without regression evidence.

## 15. COMPLETION EVIDENCE FORMAT

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

## 16. FINAL SELF-EVOLUTION RULE

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

## 17. HANDOFF

Current research handoff:
- E7.2.158–E7.2.170 completed analytically in the current reverse-analysis branch.
- The new findings are research constraints and architecture signals, not implementation authorization.
- E7.2.171 is the next target: E7.2 synthesis / Architecture Delta Review.
- First compare against existing reflection/verification/storage/governance before creating anything new.
- Repository code/tests/CI remain authoritative over this research document.
