# E7.90 — Governance Outcome & Remediation Plan Intake Contract

## Objective

Define the controlled intake boundary between an E7.89 governance outcome of REMEDIATION_REQUIRED and creation of an E7.80 remediation-plan proposal.

Intake creates a bounded proposal record. It does not approve the plan, authorize execution, grant compensation authority or mutate Ψ-Core.

## Preconditions

Plan intake MUST reference:

- exact E7.89 governance review;
- exact corrective finding;
- challenge/reconciliation provenance;
- affected lifecycle/contract;
- remediation objective;
- initial scope;
- verification criteria;
- privacy/data classification;
- known constraints and dependencies.

Only a governance review explicitly in REMEDIATION_REQUIRED may enter this intake path.

## Intake states

An intake MUST use explicit states:

- REQUESTED;
- VALIDATING;
- ACCEPTED;
- REJECTED;
- NEEDS_CLARIFICATION;
- SUPERSEDED;
- EXPIRED;
- WITHDRAWN.

ACCEPTED means accepted as a plan proposal for E7.80 evaluation. It does not mean the remediation plan itself is approved.

## Intake-to-plan binding

The resulting proposal MUST bind:

1. governance review identity;
2. finding identity;
3. remediation objective;
4. exact initial scope;
5. target/resource;
6. constraints;
7. verification criteria;
8. required evidence;
9. privacy classification;
10. proposal revision/digest.

Any material change MUST create a new proposal revision.

## Scope containment

Intake MUST NOT infer:

- additional targets;
- broader scope;
- additional data classes;
- compensation;
- execution authority;
- emergency authority.

Unknown scope MUST be marked NEEDS_CLARIFICATION or REJECTED.

## Plan handoff

When intake is ACCEPTED:

- create/link the E7.80 remediation-plan proposal;
- preserve the intake record;
- preserve the originating governance decision;
- preserve exact revision/digest linkage.

E7.80 remains responsible for plan validation, acceptance and authorization separation.

## Rejection and clarification

REJECTED MUST include reason and provenance.

NEEDS_CLARIFICATION MUST identify missing/ambiguous inputs.

No execution may begin from either state.

## Conflict handling

If the governance review and proposed intake scope conflict:

- preserve both records;
- do not silently widen/narrow the governance decision;
- route the discrepancy for governed review;
- fail closed where scope cannot be reconciled.

## Privacy boundary

Intake MUST use minimum necessary evidence.

Private payloads MUST NOT be copied into the proposal unless explicitly required and authorized.

## Authority separation

Governance outcome != plan approval
Plan intake != plan acceptance
Plan acceptance != execution authorization
Plan intake != compensation authorization
Plan intake != Ψ-Core mutation

## Recovery and replay

Intake state and proposal linkage MUST survive restart/recovery.

Identical intake MAY be idempotent when all bound identities, scope and revision are identical.

Conflicting replay MUST fail closed.

Superseded proposals remain historical records.

## Acceptance gate

E7.90 is satisfied only when implementation and tests demonstrate:

1. exact governance-to-intake provenance;
2. REMEDIATION_REQUIRED gate enforcement;
3. explicit intake state machine;
4. exact scope/target binding;
5. material revision handling;
6. controlled E7.80 handoff;
7. rejection/clarification behavior;
8. conflict preservation;
9. privacy enforcement;
10. replay/recovery integrity;
11. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.89 — Corrective Finding Governance Review & Remediation Trigger
- E7.80 — Governed Remediation Plan & Compensation Authorization
- E7.88 — External Audit Resolution, Corrective Finding & Attestation Update

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.90-r1
