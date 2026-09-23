# Gnozis Core — Integrated Reverse / Repository Work Protocol

## Status
ACTIVE from 2026-09-23.
This protocol defines the working mode in which mathematical reverse-analysis and direct repository engineering proceed in parallel. It is a workflow contract, not evidence that any implementation is verified.

## 1. Dual-track execution
Every substantial task is processed on two coupled tracks:

### Track A — Mathematical / architectural reverse
Current model → reverse question → counterexample / alternative chain → invariant or boundary → closure or backtrack

### Track B — Repository engineering
Current repository state → inspect actual code/docs/tests/CI → identify concrete gap or required change → bounded implementation → targeted tests → runtime/CI evidence → audit → repository state update

The tracks cross-check each other continuously:
Conceptual model ↔ Actual project evidence

Neither track may masquerade as evidence for the other.

## 2. Core rule
A mathematical result is not automatically an implementation requirement.
A repository mechanism is not automatically a proof of the mathematical model.
A change enters the engineering path only when the reverse-analysis or repository evidence identifies a bounded, observable requirement.

## 3. Reverse-engineering cross-check
For every important reverse node, record:
1. CONCEPTUAL RESULT — what the mathematical reverse derives.
2. PROJECT OBSERVATION — what current source/docs/tests/CI actually show.
3. MATCH / MISMATCH — whether the model and project agree.
4. COUNTEREXAMPLE — strongest known alternative or failure path.
5. CONSEQUENCE — invariant, requirement, or explicit no-change decision.
6. ENGINEERING ACTION — exact repository task, or NONE.
7. EVIDENCE REQUIRED — what must be executed/inspected before closure.
8. STATUS — OPEN / PARTIAL / REVERSE-CLOSED / IMPLEMENTED / VERIFIED / BLOCKED / UNKNOWN.
If project evidence contradicts the current model, backtrack or open a branch. Do not silently force implementation to fit the theory.

## 4. Repository-change rule
Research / Reverse → Requirement → Task → Implementation → Test → Runtime / CI Evidence → Audit → Updated Model
Do not perform broad redesign merely because a theoretical possibility was identified.
Preserve Ψ=(X,R) canonical state model; Core trust boundary; no LLM inside Core; no autonomous RuleProposal activation; evidence/status distinctions; provenance and lineage; rejected/failed/insufficient-evidence history.

## 5. One main task at a time
Select exactly one highest-priority READY engineering task for execution.
Other findings remain tracked as NEXT / BLOCKED / DEPENDS_ON / OBSERVATION / REVERSE BRANCH.

## 6. Closure rule
A reverse node may be marked REVERSE-CLOSED only when the conceptual path has been checked, relevant project evidence has been inspected, important alternative paths have been considered, and no unresolved contradiction remains within the declared scope.
REVERSE-CLOSED does not mean runtime VERIFIED.
Engineering completion requires: Implementation + targeted tests + relevant regression tests + runtime/CI evidence + scope audit.

## 7. Progress reporting
Every continuation message ends with a compact report.
Required fields:
- Mathematical reverse: XX%
- Repository engineering: XX%
- Cross-check: XX%
- Runtime/CI verification: XX%
- Current global branch: XX%
Percentages must have an explicit denominator or be described as approximate analytical progress. They must never imply test coverage or implementation completion unless supported by evidence.
Also report: CURRENT TASK, DONE, NEW EVIDENCE, OPEN, NEXT SINGLE ACTION.

## 8. Continuation format
User command «Продолжаем» means: recover the current branch and latest closed/open node; inspect relevant project evidence when the next question can be affected by implementation; perform the next reverse step; perform repository work when a bounded engineering task is justified; test/audit where applicable; update the project state; return the compact progress report.
User command «Проверяем» means prioritize evidence inspection and cross-check before introducing new architecture.

## 9. Recovery anchor
Current known continuation point:
- Project phase: R2 — Adversarial Runtime / Trust-Boundary Reverse-Analysis.
- Mathematical branch: E4.86 continuation from the established E4.81–E4.85 line.
- Evolution-boundary branch: TSZ-EV-02 / Evolution Boundary Enforcement Model.
- Current conceptual reverse node: REVERSE #15 completed; REVERSE #16 is the next conceptual node.
- Important correction: the existing project baseline already states that positive evolution-envelope runtime is not fully implemented; this must be checked against actual source before any new envelope subsystem is proposed.
- Engineering work must remain tied to actual repository evidence and current HEAD.

## 10. Source-of-truth hierarchy
1. Current source.
2. Reproducible runtime behavior and real tests/CI.
3. Accepted invariants/contracts.
4. Independent audit evidence.
5. AI reports and proposals.
6. Chat history.
AI_CONTEXT and this workflow document are handoff/context, not proof.

## 11. Required final session footer
Use this compact form in continuation reports:
[PROGRESS]
Research: <node/range + %>
Engineering: <active task + %>
Cross-check: <%>
Verification: <%>
Done: <short list>
Evidence: <new evidence / pending>
Open: <short list>
Next: <single next action>

## 12. Architectural principle
The project is treated as an information-processing and information-storage system that evolves through bounded layers.
The development loop is therefore:
Observe → Model → Implement → Test → Audit → Reverse → Compare → Update
Reverse-analysis is part of the project's engineering method itself. It is not merely a post-hoc audit.
The protected boundary is:
Finding → Candidate → Test → Verify → Governance / Authorization → Commit
A finding, reflection result, mathematical insight, stored record, or historical lineage cannot bypass this boundary.

## 13. Important distinction
Implementation correctness ≠ Model correctness
Model correctness ≠ Verification adequacy
The purpose of the dual-track workflow is to expose these gaps early, while preserving a reproducible repository history of what was actually changed and why.

## E4.99 — Falsification-strength boundary

A claim that survives executed challenges is not automatically proven. The report must distinguish:

`NO_COUNTEREXAMPLE_OBSERVED` — no counterexample was observed within the executed challenge scope;

`INSUFFICIENT_EVIDENCE` — the challenge scope, oracle, execution, or relevant blind spots are insufficient for the requested claim;

`COUNTEREXAMPLE_FOUND` — evidence contradicts the challenged claim within the declared scope;

`SUPPORTED_WITHIN_SCOPE` — the claim survived the declared challenge space with the stated limitations.

Counterexamples and rejected challenges remain historical evidence and must not be collapsed into a boolean PASS.

An adaptive challenge procedure must not silently redefine the claim, acceptance predicate, or success criterion that it is evaluating.