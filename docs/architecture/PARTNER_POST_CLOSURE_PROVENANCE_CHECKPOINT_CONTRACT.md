# E7.99 — Post-Closure Evidence Integrity Verification & Provenance Checkpoint Contract

## Objective

Define a deterministic integrity checkpoint for the complete remediation evidence chain after closure and during post-closure monitoring.

The checkpoint verifies provenance continuity and evidence integrity without rewriting historical records, changing closure status, granting execution authority or mutating Ψ-Core.

## Preconditions

The checkpoint MUST reference, where applicable:

- originating finding;
- governance decision;
- remediation plan/revision;
- validation identity/revision;
- authorization identity/revision;
- preflight/admission identity;
- execution transaction/receipt;
- outcome verification;
- closure/revision;
- monitoring record/revision;
- observation/trigger;
- reverification;
- reopening/closure decision;
- retention policy revision.

## Checkpoint states

A checkpoint MUST use explicit states:

- REQUESTED;
- CHECKING;
- VERIFIED;
- DEGRADED;
- INTEGRITY_FAILURE;
- BLOCKED;
- SUPERSEDED.

VERIFIED means all required links and integrity conditions passed according to the applicable policy.

DEGRADED means non-critical evidence limitations exist but policy permits continued observation.

INTEGRITY_FAILURE means an expected provenance or integrity condition failed.

## Verification scope

The checkpoint MUST verify:

1. every mandatory provenance link exists;
2. referenced records resolve to the expected immutable identity/revision;
3. supersession relationships are coherent;
4. evidence digests/integrity identifiers match where applicable;
5. chronological/order constraints are not violated where policy requires them;
6. authorization and execution records remain correctly separated;
7. verification and closure records remain correctly separated;
8. monitoring events remain linked to the correct closure;
9. retention/hold metadata is internally consistent;
10. no historical record was silently replaced.

## Checkpoint identity

Every successful checkpoint MUST produce a durable identity containing:

- checkpoint identity/revision;
- scope;
- evaluated record set;
- policy revision;
- result;
- limitations;
- integrity digest;
- ordering/timestamp evidence where available.

A checkpoint MUST identify exactly what evidence set it evaluated.

## Failure behavior

If a mandatory integrity condition fails:

- produce INTEGRITY_FAILURE evidence;
- preserve all available records;
- identify the broken/missing/inconsistent link;
- prevent dependent operations where policy requires;
- route the condition to governed audit/reconciliation.

The system MUST NOT silently reconstruct or invent missing historical evidence.

## Non-critical degradation

If policy allows DEGRADED status:

- identify the missing/non-critical evidence;
- record why operation remains permitted;
- record the compensating control;
- define recheck requirements.

DEGRADED MUST NOT be represented as VERIFIED.

## Recheck and supersession

A new checkpoint MAY supersede an earlier checkpoint.

Supersession MUST preserve:

- prior checkpoint identity;
- reason;
- new checkpoint identity;
- changed evidence set or policy revision.

A new checkpoint MUST NOT erase the previous result.

## Recovery and replay

Checkpoint records MUST survive restart/recovery.

Identical checkpoint requests MAY be idempotent when evaluated record set, evidence identities, policy revision and checkpoint parameters are identical.

Conflicting replay MUST fail closed.

Recovery MUST NOT fabricate VERIFIED status.

## Privacy and security

Integrity verification MUST use minimum necessary data.

Where cryptographic digests, immutable identifiers or secure references are sufficient, raw sensitive payloads MUST NOT be copied into checkpoint records.

Checkpoint access MUST remain governed.

## Authority separation

Checkpoint != remediation execution
Checkpoint != closure decision
Checkpoint != evidence creation
Checkpoint != historical repair
Checkpoint != Ψ-Core mutation

## Acceptance gate

E7.99 is satisfied only when implementation and tests demonstrate:

1. deterministic provenance verification;
2. exact evaluated evidence-set binding;
3. immutable identity/revision verification;
4. digest/integrity verification;
5. supersession consistency;
6. integrity-failure handling;
7. bounded DEGRADED mode;
8. checkpoint persistence;
9. replay/recovery integrity;
10. privacy/security controls;
11. no historical rewriting;
12. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.98 — Post-Closure Monitoring Evidence Retention & Audit Continuity
- E7.97 — Post-Closure Monitoring, Reverification & Reopening Trigger
- E7.96 — Remediation Closure & Residual Risk Governance
- E7.88 — External Audit Resolution, Corrective Finding & Attestation Update

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.99-r1
