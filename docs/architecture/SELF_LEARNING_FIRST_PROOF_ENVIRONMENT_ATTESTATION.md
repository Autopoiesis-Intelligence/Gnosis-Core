# E7.115 — First Proof Run Environment & Reproducibility Attestation Contract

## Objective

Define the environment attestation required immediately before the first actual Self-Learning proof run.

E7.115 binds execution evidence to a reproducible environment without treating environment identity as proof of implementation correctness.

## Required attestation

The attestation MUST record:

- batch ID;
- scope-lock ID;
- exact target commit SHA;
- repository/ref;
- operating-system identity;
- runtime/interpreter version;
- dependency/environment lock identity;
- test framework/tool versions;
- relevant configuration identity;
- execution tool identity/version;
- timezone/locale only where behaviorally relevant;
- evidence policy revision;
- verification-matrix revision;
- progress-calculation policy revision.

Secrets, credentials and sensitive environment values MUST NOT be captured.

## Reproducibility boundary

The environment MUST be classified:

- REPRODUCIBLE;
- CONDITIONALLY_REPRODUCIBLE;
- NON_REPRODUCIBLE;
- UNKNOWN.

The classification MUST use explicit criteria.

A NON_REPRODUCIBLE or UNKNOWN environment MUST NOT silently produce authoritative verification evidence.

## Exact-commit binding

The attestation MUST verify that the working execution target resolves to the E7.114 locked SHA.

If the runtime resolves another commit:

- execution MUST be blocked;
- the scope lock MUST be invalidated;
- no verification credit may be generated.

## Environment drift

Before execution, compare the actual environment with the attested environment.

Any material drift MUST:

- be recorded;
- trigger re-attestation or block execution;
- preserve the previous attestation;
- prevent silent continuation under a different environment.

## Determinism

Where deterministic execution is required, record:

- deterministic/random seed policy;
- relevant ordering configuration;
- dependency resolution;
- external-service assumptions;
- network requirements;
- clock/time assumptions where behaviorally relevant.

A nondeterministic dependency MUST be explicitly classified rather than hidden.

## External dependencies

External services or resources required by the proof run MUST be identified.

For each material external dependency record:

- identity;
- version/state where available;
- access mode;
- whether it is required for proof;
- whether the dependency can invalidate reproducibility.

Secrets MUST NOT be recorded.

## Attestation integrity

The attestation MUST have:

- unique attestation ID;
- creation/validation event;
- exact target commit;
- environment fingerprint or equivalent immutable identity;
- integrity identifier.

The attestation MUST be append-only.

## Recovery/replay

A replay MUST verify the attested environment before treating previous evidence as reproducible.

If the environment cannot be reproduced, historical evidence remains preserved but MUST be classified according to the applicable reproducibility policy.

## Authority separation

Environment attestation != test execution
Environment attestation != evidence acceptance
Environment reproducibility != implementation correctness
Environment identity != progress credit

## Acceptance gate

E7.115 is satisfied only when implementation and tests demonstrate:

1. complete environment identity;
2. exact-commit binding;
3. reproducibility classification;
4. material drift detection;
5. deterministic execution metadata;
6. external dependency recording;
7. secret exclusion;
8. append-only attestation integrity;
9. replay/recovery handling;
10. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.114 — First Actual Proof Run Scope Lock & Target Commit Record
- E7.113 — First Verification Batch Actual Proof Run
- E7.107 — First Verification Batch Execution Readiness Gate

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.115-r1
