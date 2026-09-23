# E7.100 — Self-Learning Contract Completion & Evidence Gate

## Objective

Define the gate that determines whether a Self-Learning contract or contract family may transition from DESIGNED to IMPLEMENTED and from IMPLEMENTED to VERIFIED.

The gate prevents documentation, static inspection or declared implementation from being treated as runtime proof.

## Status model

A contract MUST use explicit evidence states:

- DESIGNED;
- IMPLEMENTED;
- VERIFIED;
- PARTIAL;
- BLOCKED;
- SUPERSEDED.

### DESIGNED

Contract semantics are defined, but implementation evidence is insufficient.

### IMPLEMENTED

The required implementation exists in the exact target revision, but required runtime/CI evidence has not yet established the contract behavior completely.

### VERIFIED

Implementation and required tests execute successfully against the exact referenced commit/revision and satisfy the acceptance criteria.

### PARTIAL

Some acceptance criteria are implemented or verified while others remain unresolved.

### BLOCKED

Verification cannot proceed because a declared dependency, environment, authorization or evidence requirement is unavailable.

## Evidence hierarchy

Evidence MUST be weighted by strength:

1. exact-commit runtime/CI execution;
2. deterministic integration tests;
3. targeted unit/property/failure-injection tests;
4. reproducible local runtime evidence;
5. static code inspection;
6. documentation/specification.

Lower-level evidence MUST NOT be represented as equivalent to higher-level evidence.

Documentation alone MUST NEVER establish VERIFIED.

## Exact-commit binding

Every IMPLEMENTED or VERIFIED transition MUST identify:

- repository;
- branch/ref;
- exact commit SHA;
- relevant implementation paths;
- test suite/commands;
- test result;
- CI workflow/run identity where available;
- policy/contract revision.

A later commit MUST NOT retroactively serve as proof for an earlier claimed verification unless the evidence explicitly covers the later commit.

## Acceptance matrix

Each contract MUST maintain an acceptance matrix mapping:

- requirement;
- implementation location;
- test;
- expected result;
- observed result;
- evidence identity;
- status.

Unmapped mandatory requirements prevent VERIFIED.

## Runtime proof

Where a contract concerns persistence, recovery, replay, authorization, provenance, integrity, failure handling or trust boundaries, verification MUST include relevant runtime scenarios.

Examples include:

- restart/recovery;
- duplicate input;
- conflicting replay;
- malformed state;
- tampered record;
- missing provenance;
- stale authorization;
- concurrent/conflicting operation;
- failure injection;
- partial execution;
- integrity-chain break.

The applicable scenarios MUST be derived from the contract rather than assumed to be exhaustive.

## Family completion

A contract family MUST NOT be marked complete merely because each document exists.

Family completion requires:

- all mandatory contracts mapped;
- dependencies satisfied;
- all mandatory acceptance criteria mapped;
- unresolved BLOCKED/PARTIAL conditions explicitly recorded;
- required runtime/CI evidence available.

## Transition rules

Allowed transitions:

DESIGNED → IMPLEMENTED
DESIGNED → PARTIAL
IMPLEMENTED → VERIFIED
IMPLEMENTED → PARTIAL
IMPLEMENTED → BLOCKED
VERIFIED → SUPERSEDED
PARTIAL → IMPLEMENTED
PARTIAL → BLOCKED
BLOCKED → IMPLEMENTED

VERIFIED MUST NOT be downgraded silently.

Any regression MUST create an explicit evidence record and state transition.

## Self-Learning progress calculation

The project MUST distinguish at least:

- Contract Coverage % — defined contract surface;
- Implementation % — contracts with required implementation evidence;
- Verification % — contracts meeting VERIFIED gate;
- Runtime Proof % — required runtime scenarios demonstrated;
- Self-Learning Overall % — governed aggregate, with its formula/version recorded.

The percentage MUST be reproducible from the registry and evidence records.

Adding new contracts MUST NOT automatically increase Self-Learning Overall %.

## No gaming rule

The following MUST NOT increase VERIFIED or overall Self-Learning progress by themselves:

- adding documentation;
- creating empty/stub modules;
- changing status labels;
- adding tests that do not execute;
- CI configuration without successful runs;
- static inspection without required runtime proof;
- copying evidence from another commit;
- duplicating an existing contract under another name.

## Evidence failure

If required evidence is missing, contradictory or tied to the wrong commit:

- VERIFIED MUST be denied;
- status MUST remain IMPLEMENTED/PARTIAL/BLOCKED as appropriate;
- the missing evidence MUST be explicitly identified.

## Recovery and audit

Gate state and evidence MUST survive restart/recovery.

Historical progress records MUST remain reconstructable.

Corrections MUST append new evidence rather than rewrite prior evidence.

## Authority separation

Progress != implementation
Implementation != verification
Verification != self-learning capability
Percentage != capability claim
Contract completion != Ψ-Core mutation

## Acceptance gate

E7.100 is satisfied only when implementation and tests demonstrate:

1. explicit evidence state model;
2. exact-commit binding;
3. acceptance-matrix enforcement;
4. runtime-proof requirements;
5. family-completion rules;
6. valid state transitions;
7. reproducible progress calculation;
8. anti-gaming controls;
9. evidence-failure handling;
10. recovery/audit continuity;
11. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.99 — Post-Closure Evidence Integrity Verification & Provenance Checkpoint
- E7.88 — External Audit Resolution, Corrective Finding & Attestation Update
- Project Self-Learning progress registry/evidence sources

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.100-r1
