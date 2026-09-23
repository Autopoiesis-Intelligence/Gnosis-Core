# E7.91 — Remediation Plan Validation & Acceptance Gate Contract

## Objective

Define the governed validation boundary between an E7.90 remediation-plan intake proposal and an accepted remediation plan.

Validation determines whether the proposal is sufficiently complete, scoped and evidence-linked for governed plan acceptance. Validation MUST NOT authorize execution.

## Preconditions

Validation MUST reference:

- exact E7.90 intake identity;
- exact corrective finding;
- governance review identity;
- proposed remediation scope;
- target/resource identity;
- constraints and dependencies;
- success and verification criteria;
- required evidence;
- privacy/data classification;
- applicable remediation policy revision.

## Validation states

A plan validation MUST use explicit states:

- REQUESTED;
- VALIDATING;
- ACCEPTED;
- REJECTED;
- NEEDS_REVISION;
- BLOCKED;
- SUPERSEDED;
- EXPIRED.

ACCEPTED means the plan passed the defined validation criteria. It does not authorize execution or compensation.

## Validation criteria

The validator MUST verify at minimum:

1. provenance to the confirmed finding;
2. provenance to the governance decision;
3. exact target/resource binding;
4. bounded remediation scope;
5. measurable objective;
6. success criteria;
7. verification method;
8. required execution evidence;
9. dependencies and constraints;
10. privacy/disclosure requirements;
11. rollback/containment requirements where applicable;
12. policy revision compatibility.

Unknown or ambiguous critical inputs MUST result in NEEDS_REVISION or BLOCKED.

## Scope integrity

Validation MUST detect:

- scope expansion beyond governance authorization;
- undeclared targets;
- undeclared data classes;
- hidden execution authority;
- implicit compensation;
- unbounded duration;
- unverifiable success criteria.

Detected scope violations MUST NOT be normalized silently.

## Acceptance record

An accepted plan MUST bind:

- plan identity/revision;
- intake identity;
- finding identity;
- validation identity;
- validator identity;
- criteria/policy revision;
- exact scope;
- target/resource;
- success/verification criteria;
- limitations;
- digest/version.

Material plan changes MUST invalidate the previous acceptance and require revalidation.

## Rejection and revision

REJECTED MUST include reason and evidence.

NEEDS_REVISION MUST identify exact defects or missing inputs.

BLOCKED MUST identify the blocking dependency or authority condition.

No rejected, revision-required or blocked plan may enter execution authorization.

## Separation from authorization

Plan validation != execution authorization
Plan acceptance != execution authorization
Plan validation != compensation authorization
Plan validation != emergency authority
Plan validation != Ψ-Core mutation

Execution authorization remains a separate governed operation.

## Conflict handling

If plan requirements conflict with:

- governance scope;
- privacy policy;
- evidence requirements;
- lifecycle state;
- another active remediation plan;

the conflict MUST be preserved and resolved through the applicable governance path.

The validator MUST NOT silently override higher-level constraints.

## Privacy boundary

Validation MUST use minimum necessary evidence.

Sensitive/private payloads MUST NOT be copied into validation records unless explicitly required and authorized.

## Recovery and replay

Validation state MUST survive restart/recovery.

Identical validation MAY be idempotent when plan revision, criteria, validator identity and policy revision are identical.

Conflicting replay MUST fail closed.

Superseded validation records remain historical.

## Acceptance gate

E7.91 is satisfied only when implementation and tests demonstrate:

1. exact intake-to-validation provenance;
2. explicit validation state machine;
3. evidence-linked validation criteria;
4. exact scope/target integrity;
5. measurable success and verification criteria;
6. material-change revalidation;
7. rejection/revision/blocking behavior;
8. separation from execution authorization;
9. conflict preservation;
10. privacy enforcement;
11. replay/recovery integrity;
12. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.90 — Governance Outcome & Remediation Plan Intake
- E7.80 — Governed Remediation Plan & Compensation Authorization
- E7.81 — Remediation Execution Authorization & Controlled Compensation Execution
- E7.82 — Remediation Result Verification & Governed Closure

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.91-r1
