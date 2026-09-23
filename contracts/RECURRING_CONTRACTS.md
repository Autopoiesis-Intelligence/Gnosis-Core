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


## RECUR-PROJECT-DESCRIPTION-001 — Repository Project Description Synchronization

Objective:
Keep repository-facing project descriptions synchronized with the verified current project state.

Scope:
- GitHub repository description;
- README project identity/summary where applicable;
- AI_CONTEXT/STATUS references that describe repository roles;
- Research Machine ↔ Gnozis-V2 relationship;
- contract and mathematical-control-layer summary.

Rules:
1. Description is a derived representation, never the source of truth.
2. Only verified repository/runtime/CI facts may be represented as implemented capabilities.
3. Open, theoretical, hypothesis and unverified work must remain explicitly qualified.
4. Historical/archive status must not be rewritten as current implementation.
5. Changes to descriptions require a traceable contract run and exact source state.

OpenAI / ChatGPT rights:
- OpenAI/ChatGPT may be identified in project documentation as an AI participant, reviewer, architectural assistant, or contract actor only to the extent actually authorized by the project owner and available tooling.
- Such mention does NOT imply ownership, endorsement, employment, partnership, legal authority, repository ownership, copyright transfer, or permission to make decisions outside the explicitly delegated project workflow.
- OpenAI trademarks, logos, proprietary materials, model weights, APIs, or other OpenAI-controlled assets must not be represented as project assets merely because ChatGPT participated.
- Any legal/IP statement about OpenAI rights must be treated as a factual/legal claim requiring verification from the applicable OpenAI terms or an explicit project agreement; the contract itself must not invent such rights.
- Project authorship, repository ownership, and decisions remain attributable to the actual project owner/contributors unless explicitly documented otherwise.

Acceptance:
- project description matches the latest verified architecture and repository roles;
- every capability statement has provenance;
- OpenAI participation, if mentioned, is narrowly and accurately scoped;
- no unsupported legal/IP claim is introduced.


## RECUR-R2-002 — Commit-Bound Authorization Integration

Objective:
Ensure the authorization freshness verifier is not merely a standalone value check but is connected to the actual commit boundary.

Required invariant:
AuthorizationValid(A, S_current) ∧ CommitInput(S_current) = A.bound_state
must be required before mutation/commit.

A stale or tampered authorization must be rejected at the execution boundary, even if the caller bypasses the helper-level verifier.

Acceptance:
- identify the canonical commit entry point;
- integrate freshness verification at that boundary without granting the verifier mutation authority;
- add a regression test that attempts commit with stale authorization;
- add a regression test for tampered authorization;
- exact-commit CI evidence required.

Do not close based on helper-level tests alone.


## RECUR-SELF-01 — Self-Evolution
Status: ACTIVE / ORIENTATION
Purpose: preserve self-directed improvement as a permanent architectural target without granting unrestricted mutation authority.
Required path:
Generate → Test → Verify → Select → Evolve → Authorization → Commit.
Acceptance orientation:
- improvement candidates are explicit and provenance-bound;
- self-evolution cannot bypass trust boundary or commit authorization;
- no self-change is accepted solely because the system generated it.

## RECUR-SELF-02 — Self-Learning
Status: ACTIVE / ORIENTATION
Purpose: preserve self-learning as a distinct capability from code/architecture evolution.
Required path:
Observation/Experience → Evidence → Reflection → Knowledge/Rule Candidate → Test → Verify.
Acceptance orientation:
- learning artifacts retain provenance;
- evidence and knowledge are distinguishable;
- unverified observations cannot silently become authoritative rules.

## RECUR-SELF-03 — Self-Limitation
Status: ACTIVE / ORIENTATION
Purpose: make recognition of insufficient evidence and inability to safely evolve a first-class behavior.
Required invariant:
InsufficientEvidence → NoCommit.
The system must be able to preserve uncertainty rather than force an evolution or learning outcome.

These three recurring contracts are architectural orientations and are excluded from the current ~49% Global Contract Progress until a documented weighting/acceptance scheme is established.


## RECUR-SELF-01A — Self-Evolution Candidate Integrity
Status: ACTIVE / MACHINE-TESTABLE

Invariant:
A self-evolution candidate MUST be explicit, provenance-bound, and distinguishable from an executed change.

Required predicates:
1. candidate_id is unique within its instance/lineage scope;
2. candidate carries parent/current state identity;
3. candidate carries provenance identity;
4. candidate has test/evidence references before authorization;
5. candidate generation alone never implies authorization or commit.

Formal:
CandidateValid(c) =>
  Unique(c.id)
  ∧ Bound(c.parent_state)
  ∧ Bound(c.provenance)
  ∧ HasEvidence(c)
  ∧ ¬AuthorizedByGeneration(c)

Acceptance:
- tests cover missing provenance;
- tests cover state/lineage mismatch;
- tests cover attempted commit of an unverified candidate;
- tests prove generation cannot directly mutate canonical state.

## RECUR-SELF-02A — Self-Learning Provenance Integrity
Status: ACTIVE / MACHINE-TESTABLE

Invariant:
A learning artifact cannot become an authoritative rule without evidence and verification.

Formal:
AuthoritativeRule(r) =>
  Provenance(r)
  ∧ Evidence(r)
  ∧ Verified(r)

Acceptance:
- observation without evidence remains non-authoritative;
- evidence without verification remains non-authoritative;
- provenance mismatch is rejected;
- verified learning artifact can enter the normal candidate pipeline.

## RECUR-SELF-03A — Self-Limitation No-Commit
Status: ACTIVE / MACHINE-TESTABLE

Invariant:
Insufficient or contradictory evidence must produce a hard no-commit result.

Formal:
InsufficientEvidence(c) ∨ ContradictoryEvidence(c)
=> ¬Commit(c)

Acceptance:
- insufficient evidence test;
- contradictory evidence test;
- explicit rejection reason/provenance;
- no durable mutation on rejected path.

These acceptance criteria are additive and do not supersede P0 persistence/recovery or commit-bound authorization gates.
