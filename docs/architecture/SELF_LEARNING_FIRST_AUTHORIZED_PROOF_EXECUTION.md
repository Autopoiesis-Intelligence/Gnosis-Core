# E7.117 — First Authorized Proof Execution Record Contract

## Objective

Define the authoritative runtime record for the first proof execution after E7.116 authorization.

E7.117 MUST capture the actual transition from AUTHORIZED to EXECUTING and the terminal outcome of the frozen proof run.

## Preconditions

Execution MUST reference:

- valid E7.114 scope lock;
- valid E7.115 environment attestation;
- valid E7.116 authorization;
- exact target commit;
- immutable batch identity.

No execution record may be marked EXECUTING without a valid authorization.

## Execution lifecycle

The runtime record MUST support:

- AUTHORIZED;
- STARTING;
- EXECUTING;
- COMPLETED;
- FAILED;
- INTERRUPTED;
- ABORTED;
- BLOCKED.

Transitions MUST be explicit and append-only.

## Start record

At execution start record:

- execution ID;
- batch ID;
- authorization ID;
- scope-lock ID;
- environment-attestation ID;
- exact target commit;
- command/test identity;
- start event;
- execution actor/tool identity;
- integrity identifier.

The start event MUST establish that execution actually began.

## Runtime capture

For each proof path record:

- sequence/order;
- command/test identity;
- start/end event;
- exit/result state;
- stdout/stderr artifact reference where applicable;
- artifact digest;
- expected result;
- observed result;
- criterion IDs;
- failure classification if applicable.

Secrets MUST NOT be persisted.

## Terminal state

The execution MUST terminate explicitly as:

- COMPLETED;
- FAILED;
- INTERRUPTED;
- ABORTED;
- BLOCKED.

A missing terminal event MUST be treated as unresolved, not successful.

## Failure and interruption

On failure/interruption:

- preserve all completed records;
- preserve partial evidence;
- record failure/interruption reason where available;
- do not synthesize successful output;
- prevent automatic verification credit.

Retries MUST create a distinct execution attempt or explicitly governed continuation record.

## Exact-commit enforcement

At runtime verify that the executing source resolves to the locked target SHA.

If mismatch occurs:

- stop execution;
- record COMMIT_MISMATCH;
- invalidate the authorization;
- preserve all evidence;
- grant no verification credit.

## Atomic authorization linkage

The execution record MUST reference the authorization that permitted it.

An execution without a valid authorization MUST be classified UNAUTHORIZED and MUST NOT be accepted as proof.

## Replay and idempotency

Replaying an identical execution request MUST NOT overwrite the original execution record.

Duplicate execution identities MUST be rejected or explicitly linked as retries.

Conflicting records MUST remain preserved and enter conflict handling.

## Progress boundary

E7.117 MUST NOT modify:

- Implementation %;
- Verification %;
- Runtime Proof %;
- Self-Learning Overall %.

Progress changes remain downstream of E7.109/E7.110 and later review/closure gates.

## Recovery

After restart/recovery:

- execution state MUST be reconstructable;
- completed proof-path records MUST remain;
- unresolved execution MUST remain unresolved;
- recovery MUST NOT fabricate completion.

## Acceptance gate

E7.117 is satisfied only when implementation and tests demonstrate:

1. authorization linkage;
2. actual start capture;
3. explicit lifecycle;
4. runtime command/test capture;
5. terminal-state enforcement;
6. exact-commit runtime verification;
7. failure/interruption preservation;
8. unauthorized-execution rejection;
9. duplicate/replay safety;
10. recovery integrity;
11. zero direct progress effect;
12. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.116 — First Proof Run Preflight Final Gate & Execution Authorization
- E7.115 — First Proof Run Environment & Reproducibility Attestation
- E7.114 — First Actual Proof Run Scope Lock & Target Commit Record
- E7.108 — First Verification Batch Execution Record & Evidence Capture

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.117-r1
