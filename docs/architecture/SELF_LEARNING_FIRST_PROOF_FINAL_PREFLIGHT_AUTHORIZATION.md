# E7.116 — First Proof Run Preflight Final Gate & Execution Authorization Contract

## Objective

Define the final fail-closed authorization boundary immediately before the first actual Self-Learning proof run.

E7.116 MUST authorize execution only when the frozen scope, exact commit, environment attestation, evidence path and required policies are all valid.

## Required inputs

The authorization MUST reference:

- E7.105 immutable baseline;
- E7.106 frozen candidate selection;
- E7.107 readiness state;
- E7.114 scope lock;
- E7.115 environment attestation;
- E7.108 evidence capture configuration;
- E7.109 acceptance policy;
- E7.110 reconciliation policy;
- E7.111 audit path;
- E7.112 closure path;
- exact target commit;
- active contract/policy revisions.

## Final preflight checks

Before authorization verify:

1. repository/ref resolves to locked SHA;
2. scope lock is valid and unexpired where expiry is defined;
3. selected criteria and commands are unchanged;
4. required implementation/test/runtime paths exist at the target SHA;
5. environment attestation matches actual execution environment;
6. required dependencies are available;
7. evidence capture is writable/available and integrity-capable;
8. no prohibited secrets will be captured;
9. stop/fail-closed conditions are configured;
10. progress remains frozen before execution;
11. required audit/reconciliation/closure paths are available.

Every check MUST have an explicit PASS/FAIL/BLOCKED result.

## Authorization states

The gate MUST use:

- NOT_READY;
- READY;
- AUTHORIZED;
- REVOKED;
- EXPIRED;
- BLOCKED.

Only AUTHORIZED may start execution.

Authorization MUST reference the exact scope-lock ID, environment attestation ID and target SHA.

## Revocation

Authorization MUST be revoked if:

- target commit changes;
- scope changes;
- material environment drift occurs;
- evidence capture becomes unavailable;
- required policy revision changes;
- a mandatory preflight check becomes invalid.

Revocation MUST prevent further execution under the revoked authorization.

## Atomicity

Authorization and execution start MUST be linked so that an execution cannot claim authorization that did not exist.

If atomic linking cannot be guaranteed, execution MUST remain unauthorised and produce no verification credit.

## No progress effect

Creating or granting authorization MUST NOT change any progress metric.

Only accepted evidence and subsequent reconciliation can affect progress.

## Audit record

The authorization record MUST contain:

- authorization ID;
- batch ID;
- scope-lock ID;
- environment-attestation ID;
- exact target SHA;
- preflight results;
- policy revisions;
- authorizing identity;
- authorization timestamp/order metadata;
- integrity identifier.

## Recovery/replay

Authorization records MUST be durable and append-only.

Replaying an authorization request MUST be idempotent for identical inputs.

Conflicting authorization attempts MUST fail closed.

Recovery MUST NOT transform READY/REVOKED/BLOCKED into AUTHORIZED without revalidation.

## Acceptance gate

E7.116 is satisfied only when implementation and tests demonstrate:

1. complete final preflight;
2. explicit check results;
3. exact-commit binding;
4. scope/environment binding;
5. evidence-path validation;
6. fail-closed authorization states;
7. revocation;
8. authorization/execution linkage;
9. no progress effect;
10. durable audit record;
11. deterministic replay/recovery;
12. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.115 — First Proof Run Environment & Reproducibility Attestation
- E7.114 — First Actual Proof Run Scope Lock & Target Commit Record
- E7.107 — First Verification Batch Execution Readiness Gate
- E7.108 — First Verification Batch Execution Record & Evidence Capture

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.116-r1
