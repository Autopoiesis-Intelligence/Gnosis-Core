# E7.88 — External Audit Resolution, Corrective Finding & Attestation Update Contract

## Objective

Define the governed transition from a reconciled external audit challenge to a corrective finding and, where justified, a controlled update of the affected attestation.

Resolution MUST preserve the original challenge, evidence, package and prior attestation as immutable historical records.

## Preconditions

A resolution MUST reference:

- exact challenge identity;
- exact challenged package/evidence;
- reconciliation record;
- conflicting or supporting evidence;
- resolution authority;
- applicable audit policy revision;
- affected attestation, if any;
- disclosure/privacy classification.

## Resolution states

A corrective finding MUST use explicit states:

- PROPOSED;
- VALIDATING;
- CONFIRMED;
- REJECTED;
- DISPUTED;
- SUPERSEDED;
- CLOSED.

Only CONFIRMED findings may drive an attestation update.

## Finding classification

A confirmed finding MUST classify the outcome, at minimum, as:

- NO_DEFECT_FOUND;
- EVIDENCE_DEFICIENCY;
- PROVENANCE_DEFICIENCY;
- SCOPE_DEFICIENCY;
- PROCESS_DEFICIENCY;
- MATERIAL_INCONSISTENCY;
- POLICY_VIOLATION;
- UNRESOLVED.

The classification MUST describe evidence-supported facts, not inferred intent.

## Resolution record

The resolution MUST bind:

1. challenge identity;
2. exact disputed claim;
3. evidence considered;
4. reconciliation result;
5. finding classification;
6. finding rationale;
7. corrective action requirement, if any;
8. affected attestation;
9. resolution authority;
10. limitations/uncertainty;
11. revision and digest.

## Attestation update

An attestation update MUST create a new attestation revision or a formally governed withdrawal/supersession record.

The prior attestation MUST remain immutable and queryable.

The new attestation MUST explicitly reference:

- predecessor attestation;
- corrective finding;
- changed verification scope/criteria;
- material changes;
- effective revision;
- remaining limitations.

An update MUST NOT silently overwrite the previous attestation.

## Corrective action separation

A corrective finding MAY require remediation, but finding confirmation MUST NOT itself authorize remediation execution.

If remediation is required, the system MUST enter the E7.80/E7.81 governed remediation path.

## No retroactive evidence mutation

Resolution MUST NOT:

- rewrite source evidence;
- alter historical execution evidence;
- modify the original audit package;
- erase challenge history;
- change historical authorization records.

If an earlier record was defective, the correction MUST be represented as a new governed record.

## Rejection and unresolved outcomes

REJECTED means the finding was not confirmed under the applicable criteria.

DISPUTED means material disagreement remains.

UNRESOLVED findings MUST preserve the uncertainty and MUST NOT be represented as confirmed defects or confirmed absence of defects.

## Privacy and disclosure

Resolution records MUST contain only the minimum evidence required.

Any new disclosure required to resolve the challenge MUST use a separate authorization path.

Private source material MUST NOT be copied into general audit records unnecessarily.

## Recovery and replay

Finding and attestation-update state MUST survive restart/recovery.

Identical resolution requests MAY be idempotent when all bound identities and inputs are identical.

Conflicting replay MUST fail closed.

## Authority separation

Challenge resolution != evidence mutation
Finding confirmation != remediation authorization
Attestation update != execution authorization
Attestation update != Core mutation
Correction != history deletion

## Acceptance gate

E7.88 is satisfied only when implementation and tests demonstrate:

1. exact challenge-to-resolution provenance;
2. explicit finding state machine;
3. evidence-based classification;
4. immutable prior attestation;
5. controlled attestation supersession/withdrawal;
6. remediation separation;
7. no retroactive evidence mutation;
8. unresolved/disputed handling;
9. privacy enforcement;
10. replay/recovery integrity;
11. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.86 — External Auditor Verification & Attestation Boundary
- E7.87 — External Audit Challenge, Dispute & Evidence Reconciliation
- E7.80 — Governed Remediation Plan & Compensation Authorization
- E7.82 — Remediation Result Verification & Governed Closure

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.88-r1
