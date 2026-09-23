# E7.14 — End-to-End Learning Execution and Replay Contract

## Purpose

Prove that the complete governed self-learning path can execute, persist its provenance, survive restart/replay, and re-evaluate invalidated learning material without bypassing Core verification or governance.

## Canonical execution path

Agent/Observation
-> Identity
-> Scope
-> Provenance
-> SourceRevision
-> Independence
-> Quarantine
-> Finding
-> Counterexample/Challenge
-> Candidate/RuleProposal
-> ShadowEvaluation
-> CoreVerification
-> Governance
-> AcceptedTransition
-> NewObservation.

## Determinism

Given the same:

- immutable input revisions;
- agent identity/revision;
- contract revisions;
- Core parent state;
- evidence set;
- policy configuration;

the learning decision MUST be reproducible, or any nondeterministic component MUST be explicitly recorded as part of the execution evidence.

## Persistence

A completed learning cycle MUST persist enough information to reconstruct:

1. source revisions;
2. agent identity and capability scope;
3. provenance graph;
4. evidence independence classification;
5. generated findings/counterexamples;
6. candidate/proposal lineage;
7. shadow evaluation result;
8. verification result;
9. governance decision;
10. resulting state transition, if accepted.

## Replay

Replay MUST NOT create a second epistemic fact merely because the execution receives a new session or transport identifier.

Replay of an unchanged valid cycle MUST produce an equivalent decision record.

Replay after source revocation, supersession, parent-state change or contract revision change MUST enter re-evaluation rather than silently reproduce the former acceptance.

## Failure injection

The acceptance suite MUST exercise at minimum:

- unknown/revoked agent;
- stale source;
- duplicate event;
- replayed event;
- shared-origin evidence;
- missing provenance;
- parent-state mismatch;
- failed shadow evaluation;
- failed Core verification;
- rejected governance decision;
- persistence interruption;
- restart during learning;
- superseded source after prior acceptance.

Failures MUST preserve evidence and MUST NOT partially activate an unverified learning transition.

## No bypass invariant

LearningExecution -> CanonicalState is permitted only through the existing Verification -> Governance -> Commit boundary.

No agent, dataset, reflection result or replay operation may create a direct mutation path.

## Acceptance

E7.14 is complete only when the full path is executable in an isolated test environment, persisted, replayable, failure-injected, and demonstrably unable to bypass the trust boundary.

Status: DESIGNED / NOT_IMPLEMENTED.
