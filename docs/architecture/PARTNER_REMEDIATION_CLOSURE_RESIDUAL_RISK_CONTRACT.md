# E7.96 — Remediation Closure & Residual Risk Governance Contract

## Objective

Define the governed boundary between E7.95 outcome verification and final remediation closure.

Closure MUST be evidence-based and MUST preserve residual risk, unresolved obligations, limitations and historical execution/verification records.

## Preconditions

Closure MUST reference:

- exact remediation plan/revision;
- governance decision;
- authorization/revision;
- execution receipt(s);
- latest outcome verification;
- reconciliation records, if any;
- residual risk assessment;
- outstanding obligations;
- applicable closure policy revision.

## Closure states

A closure record MUST use explicit states:

- REQUESTED;
- REVIEWING;
- CLOSED;
- CONDITIONALLY_CLOSED;
- REOPENED;
- BLOCKED;
- SUPERSEDED.

CLOSED means all required closure criteria were satisfied under the applicable policy.

CONDITIONALLY_CLOSED means the remediation objective was accepted with explicitly recorded residual obligations or bounded risk.

## Closure eligibility

FULL_SUCCESS MAY be eligible for CLOSED only when all mandatory closure criteria are satisfied.

PARTIAL_SUCCESS MUST NOT be silently represented as CLOSED.

INCONCLUSIVE MUST NOT be represented as CLOSED unless a policy explicitly permits conditional closure with the uncertainty preserved.

NO_SUCCESS MUST NOT be represented as successful closure.

Any mandatory unresolved safety, security, privacy, governance or verification condition MUST block closure unless an explicit governed exception applies.

## Residual risk

Every non-zero residual risk MUST record:

- risk identity;
- affected scope;
- evidence basis;
- severity/materiality classification under policy;
- owner/authority;
- mitigation or monitoring requirement;
- review/reassessment condition;
- effective period;
- status.

Residual risk MUST NOT be deleted merely to enable closure.

## Outstanding obligations

Closure MUST identify any remaining:

- remediation tasks;
- monitoring requirements;
- evidence collection;
- re-verification;
- disclosure obligations;
- contractual obligations;
- governance reviews.

Each obligation MUST have a state and provenance.

## Conditional closure

CONDITIONALLY_CLOSED MUST include:

- exact condition(s);
- responsible authority;
- deadline/review window where applicable;
- monitoring requirement;
- trigger for reopening;
- residual-risk identity.

Conditional closure MUST NOT be presented as equivalent to unconditional CLOSED.

## Reopening

A closed remediation MUST be REOPENED when material new evidence demonstrates:

- outcome criteria were not actually satisfied;
- prior verification was materially defective;
- a material residual risk was omitted;
- a new conflict invalidates closure;
- required follow-up obligations were not met.

Reopening MUST preserve the previous closure record.

## Closure evidence

The closure record MUST bind:

1. latest verified outcome;
2. closure criteria/policy revision;
3. residual-risk assessment;
4. outstanding obligations;
5. closure authority;
6. closure identity/revision;
7. limitations;
8. integrity digest.

Closure MUST distinguish observed facts from governance judgment.

## Privacy and security

Closure records MUST use minimum necessary evidence.

Sensitive evidence MUST remain referenced rather than copied when possible.

## Recovery and replay

Closure state MUST survive restart/recovery.

Identical closure requests MAY be idempotent when all referenced revisions, criteria, risk state and authority are identical.

Conflicting replay MUST fail closed.

Recovery MUST NOT fabricate CLOSED state.

## Authority separation

Verification != closure
Closure != deletion
Conditional closure != full closure
Closure != history mutation
Residual risk acceptance != execution authorization
Closure != Ψ-Core mutation

## Acceptance gate

E7.96 is satisfied only when implementation and tests demonstrate:

1. exact verification-to-closure provenance;
2. explicit closure state machine;
3. outcome-dependent closure eligibility;
4. residual-risk preservation;
5. outstanding-obligation tracking;
6. conditional closure controls;
7. governed reopening;
8. privacy/security enforcement;
9. replay/recovery integrity;
10. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.95 — Remediation Execution Result Reconciliation & Outcome Verification
- E7.82 — Remediation Result Verification & Governed Closure
- E7.89 — Corrective Finding Governance Review & Remediation Trigger
- E7.88 — External Audit Resolution, Corrective Finding & Attestation Update

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.96-r1
