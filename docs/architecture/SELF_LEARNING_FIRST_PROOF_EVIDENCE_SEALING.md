# E7.118 — First Proof Runtime Evidence Integrity & Artifact Sealing Contract

## Objective

Define the integrity boundary for runtime evidence produced by E7.117 before evidence acceptance, reconciliation or progress calculation.

E7.118 MUST seal captured artifacts without changing their substantive results.

## Required inputs

The sealing process MUST reference:

- batch ID;
- execution ID;
- authorization ID;
- scope-lock ID;
- environment-attestation ID;
- exact target commit;
- execution terminal state;
- evidence policy revision.

## Artifact inventory

Every proof artifact MUST have an inventory record containing:

- artifact ID;
- artifact type;
- producing execution ID;
- criterion IDs;
- creation event/order metadata;
- storage/reference location;
- byte/content digest;
- size where applicable;
- capture status;
- sensitivity classification;
- integrity status.

Missing or ambiguous provenance MUST prevent sealing.

## Sealing

Sealing MUST produce an immutable evidence manifest containing:

- execution identity;
- exact target SHA;
- artifact inventory;
- artifact digests;
- evidence-policy revision;
- manifest creation event;
- manifest integrity identifier.

The manifest MUST be append-only.

Sealing MUST NOT modify the underlying evidence content.

## Integrity verification

Verification MUST detect:

- artifact mutation;
- artifact replacement;
- artifact deletion;
- duplicate identity;
- digest mismatch;
- provenance mismatch;
- execution/criterion mismatch.

Any integrity failure MUST produce a fail-closed result for the affected evidence.

## Sensitive data

Secrets, credentials and unrelated private data MUST NOT enter the evidence manifest.

If sensitive material is accidentally captured:

- preserve the incident record;
- prevent publication/promotion of the affected artifact;
- apply the project's approved redaction/quarantine process;
- do not silently rewrite the historical evidence record.

## Completeness

The manifest MUST distinguish:

- CAPTURED;
- SEALED;
- MISSING;
- PARTIAL;
- QUARANTINED;
- INVALID.

An artifact marked MISSING/PARTIAL/QUARANTINED/INVALID MUST NOT be represented as complete evidence.

## Replay

Replaying sealing against the same immutable artifacts MUST produce the same manifest identity under the same sealing policy.

A changed artifact MUST produce a different digest/manifest or fail.

## Evidence vs acceptance

E7.118 seals evidence; it does not decide whether the evidence proves a criterion.

Acceptance remains governed by E7.109.

Reconciliation remains governed by E7.110.

Independent review remains governed by E7.111.

## Progress boundary

E7.118 MUST NOT change Self-Learning progress.

Sealing evidence is not evidence acceptance.

## Acceptance gate

E7.118 is satisfied only when implementation and tests demonstrate:

1. complete artifact inventory;
2. exact execution/commit provenance;
3. immutable manifest;
4. mutation/replacement/deletion detection;
5. duplicate/provenance conflict detection;
6. sensitive-data handling;
7. completeness states;
8. deterministic replay;
9. separation from acceptance/progress;
10. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.117 — First Authorized Proof Execution Record
- E7.109 — First Verification Batch Evidence Acceptance & Criterion Promotion Gate
- E7.110 — First Verification Batch Result Reconciliation & Progress Recalculation Gate
- E7.111 — First Verification Batch Post-Execution Audit & Independent Evidence Review

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.118-r1
