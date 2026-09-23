# E7.10 — Governed Self-Learning Feedback Loop

## Purpose
Define the bounded path by which observations, partner/agent evidence, reflection findings and counterexamples can improve future behavior without directly rewriting canonical state or granting authority.

## Learning path
Observation -> Provenance -> Finding -> Counterexample/Challenge -> Candidate/RuleProposal -> Shadow Evaluation -> Verification -> Governance -> Accepted Rule/Transition -> New Observation.

External and partner learning uses:
SourceRevision + Evidence + Scope + AuditStatus + RevocationStatus.

## Non-authority boundary
LearningData != CoreState
Finding != Truth
RuleProposal != ActiveRule
ShadowResult != ProductionVerification
AgentConsensus != Proof
HistoricalSuccess != CurrentAuthorization

## Freshness
Every candidate/proposal derived from mutable external or environmental evidence MUST bind to the relevant source revision and state context.
Stale material must be rejected, re-evaluated, or explicitly retained as historical evidence.

## Independence
Evidence originating from copied repositories, common datasets, shared models, common external sources or known common ancestry MUST NOT be counted as independent merely because it arrives through different agents.

## Feedback safety
Negative feedback, counterexamples and failed proposals remain first-class evidence. Rejection MUST NOT delete the underlying evidence.

## Learning activation
Self-learning may change the candidate/test/rule hypothesis space. It may not directly activate a production rule or mutate canonical state without the existing verification and governance gates.

## Acceptance
Implementation is accepted only when the learning path is provenance-preserving, revision-bound, replayable, resistant to stale/replayed evidence, and incapable of bypassing Core verification/governance.

Status: DESIGNED / PARTIALLY COVERED BY EXISTING REFLECTION + PROVENANCE COMPONENTS; runtime end-to-end proof NOT_IMPLEMENTED.