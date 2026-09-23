# E7.103 — Self-Learning Evidence-to-Contract Verification Matrix Contract

## Objective

Define the authoritative mapping between Self-Learning contract requirements and the concrete implementation, tests and evidence required to transition each criterion through IMPLEMENTED and VERIFIED.

The matrix MUST expose proof gaps rather than hide them inside aggregate percentages.

## Matrix record

Each criterion MUST identify:

- contract/task ID;
- contract revision;
- criterion ID;
- requirement statement;
- implementation location;
- test type;
- test path/name;
- required runtime scenario;
- expected result;
- evidence record ID;
- exact commit SHA;
- CI/run identity where applicable;
- current evidence state;
- blocking dependency;
- verification status.

## Criterion states

Each criterion MUST use:

- UNMAPPED;
- MAPPED;
- IMPLEMENTED;
- VERIFIED;
- PARTIAL;
- BLOCKED;
- CONFLICT;
- SUPERSEDED.

A contract MUST NOT be VERIFIED while any mandatory criterion remains UNMAPPED, PARTIAL, BLOCKED or CONFLICT unless an explicit policy exception is recorded.

## Mapping requirements

Every mandatory contract requirement MUST map to at least one proof path.

Proof paths SHOULD distinguish:

- unit/property test;
- integration test;
- failure-injection test;
- recovery/restart test;
- replay/idempotency test;
- CI execution;
- runtime observation;
- external audit.

A static inspection may map a structural criterion but cannot replace runtime proof where runtime behavior is required.

## Proof gap classification

Each unmapped or insufficient criterion MUST receive one explicit gap class:

- NO_IMPLEMENTATION;
- NO_TEST;
- NO_RUNTIME_PROOF;
- WRONG_COMMIT;
- FAILED_TEST;
- MISSING_EVIDENCE;
- CONFLICTING_EVIDENCE;
- BLOCKED_DEPENDENCY;
- POLICY_EXCEPTION.

Gap closure MUST reference new evidence.

## Batch verification

The matrix MUST support bounded verification batches.

A batch MUST define:

- selected contracts/criteria;
- exact target commit;
- test scope;
- required environment;
- evidence policy revision;
- expected outputs;
- acceptance boundary.

A failed criterion MUST NOT invalidate unrelated evidence unless the contract dependency graph requires it.

## Verification promotion

A criterion may transition to VERIFIED only when:

1. implementation exists at exact target commit;
2. mapped test/evidence executed;
3. observed result satisfies expected result;
4. evidence is ACCEPTED in the E7.101/E7.102 pipeline;
5. all criterion dependencies are satisfied;
6. no unresolved conflict invalidates the evidence.

A contract may transition to VERIFIED only when all mandatory criteria satisfy the gate.

## Progress integration

The matrix MUST feed E7.101 progress calculation.

It MUST NOT count:

- unmapped criteria;
- rejected evidence;
- wrong-commit evidence;
- unresolved conflicts;
- documentation-only proof for runtime criteria.

Adding a mapping without proof MUST NOT increase Verification %.

## Regression

If a previously VERIFIED criterion fails under a new applicable revision:

- preserve the prior VERIFIED evidence;
- create a new criterion/evidence state;
- mark the current criterion as requiring re-verification;
- do not erase historical proof.

## Recovery and replay

Matrix state MUST survive restart/recovery.

Duplicate mapping submissions MUST be idempotent.

Conflicting mappings MUST fail closed.

Recovery MUST NOT fabricate VERIFIED criteria.

## Authority separation

Matrix != implementation
Matrix != test execution
Matrix != evidence acceptance
Matrix != progress manipulation
Matrix != Ψ-Core mutation

## Acceptance gate

E7.103 is satisfied only when implementation and tests demonstrate:

1. complete criterion mapping;
2. exact implementation/test binding;
3. explicit proof-gap classification;
4. bounded verification batches;
5. deterministic promotion rules;
6. progress integration;
7. regression preservation;
8. duplicate/conflict handling;
9. recovery integrity;
10. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.102 — Self-Learning Evidence Ingestion & Acceptance Pipeline
- E7.101 — Self-Learning Evidence Registry & Reproducible Progress Ledger
- E7.100 — Self-Learning Contract Completion & Evidence Gate

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.103-r1
