# E7.77 — External Collaboration Execution Evidence & Result Reconciliation Contract

## Objective

Define the evidence boundary after an authorized external collaboration action.

E7.77 records what was attempted, what authorization permitted, what actually happened, and whether the observed result matches the authorized scope.

This contract does not authorize, execute, retry, publish, invite, change permissions, mutate Ψ-Core, or repair historical evidence.

## Required chain

The evidence record MUST bind:

Proposal -> Review -> Authorization -> Execution Attempt -> Result -> Reconciliation

Each link MUST reference the exact prior artifact revision or digest where available.

## Required execution evidence

An execution evidence record MUST contain:

- evidence ID;
- authorization identity/digest;
- accepted review identity/digest;
- exact proposal revision;
- action class;
- target resource identity;
- authorized scope;
- executor identity;
- execution attempt identity;
- execution ordering evidence;
- observed result/status;
- target before/after revision or digest where available;
- privacy/disclosure classification;
- reconciliation status;
- provenance references;
- evidence digest.

## Result states

The external adapter MUST distinguish at least:

- NOT_ATTEMPTED;
- ATTEMPTED;
- SUCCEEDED;
- FAILED;
- PARTIAL;
- UNKNOWN;
- REJECTED_BY_BOUNDARY.

UNKNOWN MUST NOT be interpreted as success.

PARTIAL MUST NOT be interpreted as full completion.

## Reconciliation

Reconciliation MUST compare the observed result with:

1. the exact authorization;
2. the requested action;
3. the authorized target;
4. the authorized scope;
5. the expected preconditions;
6. the observed target revision/digest where available.

Possible reconciliation states:

- RECONCILED;
- MISMATCH;
- INCOMPLETE;
- UNKNOWN;
- REJECTED.

A mismatch MUST NOT silently become a successful execution record.

## Fail-closed rules

The evidence layer MUST NOT mark an execution RECONCILED when:

- authorization is missing, revoked or stale;
- proposal/review linkage is inconsistent;
- target identity differs;
- observed scope exceeds authorized scope;
- privacy classification is missing or conflicting;
- result evidence is insufficient;
- before/after identity is inconsistent;
- duplicate/conflicting execution identities are detected.

Unknown conditions resolve to non-reconciled evidence.

## Idempotency and replay

An execution attempt identity MUST be unique within its authorization scope.

An exact duplicate observation MAY be recorded idempotently.

A conflicting duplicate MUST fail closed and preserve both the original evidence and the conflict finding.

Evidence MUST NOT rewrite an earlier result to conceal a conflict.

## Failure and recovery

Recovery MUST preserve execution evidence and reconciliation state.

A restart MUST NOT convert FAILED, PARTIAL or UNKNOWN into SUCCEEDED without new evidence.

No recovery path may silently retry an external action.

Retries, if authorized separately, MUST create a new execution-attempt identity and preserve linkage to the previous attempt.

## Privacy boundary

Evidence MUST contain metadata/digests sufficient for reconstruction without copying private payloads unnecessarily.

Private source payloads MUST NOT be placed into common collaboration evidence unless explicitly authorized as shareable.

A public target does not authorize private evidence disclosure.

## Authority separation

Execution evidence is evidence, not authority.

A successful external action MUST NOT:

- grant new capabilities;
- broaden partner scope;
- authorize future actions;
- mutate Ψ-Core;
- alter governance records retroactively.

Any subsequent capability or Core change requires its own governed contract path.

## Acceptance gate

E7.77 is satisfied only when implementation and tests demonstrate:

1. exact Proposal -> Review -> Authorization linkage;
2. exact target/action/scope binding;
3. explicit execution result states;
4. reconciliation against observed target state;
5. fail-closed mismatch handling;
6. duplicate/conflicting replay protection;
7. recovery without result inflation or history rewrite;
8. privacy-boundary enforcement;
9. separation of evidence from authority;
10. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.46 — Governed Proposal Review / Acceptance Record
- E7.48 — Controlled Execution Evidence / Mutation Receipt
- E7.75 — Governed Collaboration Proposal Review & Acceptance
- E7.76 — Collaboration Execution Authorization & External Action Boundary

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.77-r1
