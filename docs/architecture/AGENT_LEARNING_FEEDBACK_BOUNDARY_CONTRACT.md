# E7.13 — Agent Learning Feedback Boundary Contract

## Purpose

Connect accepted partner/agent inputs to the governed self-learning loop without allowing an agent, partner repository, dataset, or dialogue to bypass provenance, freshness, independence, verification, or governance.

## Input path

AgentSubmission -> IdentityCheck -> ScopeCheck -> ProvenanceCheck -> RevisionCheck -> IndependenceAnalysis -> EvidenceQuarantine -> LearningCandidate -> ShadowEvaluation -> CoreVerification -> Governance.

No step may be skipped for convenience.

## Agent contribution classes

An agent may submit:

- observation;
- evidence;
- counterexample;
- test;
- candidate;
- rule proposal;
- contract challenge;
- dataset revision.

Submission type does not imply authority.

## Capability boundary

Let C be granted capabilities and R requested capabilities.

R != C.

A submission is accepted only within the intersection of:

GrantedScope ∩ ContractScope ∩ VerifiedInterface.

## Dataset boundary

A partner dataset is immutable by revision and is treated as external evidence.

PartnerDatasetRevision -> LearningCandidate is permitted.

PartnerDatasetRevision -> CanonicalState is forbidden.

## Feedback semantics

Accepted evidence may change the hypothesis space, trigger tests, create counterexamples, or propose rules.

It cannot directly:

- activate a rule;
- modify canonical state;
- grant authority;
- alter audit history;
- rewrite provenance;
- suppress a counterexample.

## Agent disagreement

Conflicting agent submissions remain separate evidence branches until Core verification resolves their relevance.

Consensus is not required for a candidate to be tested, and consensus is not sufficient for acceptance.

## Failure behavior

Unknown identity, revoked identity, invalid provenance, stale revision, unresolved independence, scope violation, malformed evidence, or failed verification MUST fail closed into quarantine/rejection.

## Acceptance

E7.13 is complete only when an agent submission can traverse the full learning boundary deterministically, with persisted provenance and no direct mutation path to canonical state.

Status: DESIGNED / NOT_IMPLEMENTED.
