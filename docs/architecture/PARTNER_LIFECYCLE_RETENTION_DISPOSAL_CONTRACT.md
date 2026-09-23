# E7.84 — Lifecycle Retention, Evidence Preservation & Controlled Data Disposal Contract

## Objective

Define the post-closure boundary for retaining provenance/audit evidence and, where legally or operationally required, disposing of eligible data without corrupting the historical record.

Retention and disposal are separate governed actions.

Closure or termination alone MUST NOT authorize deletion.

## Preconditions

A retention/disposal decision MUST reference:

- exact collaboration lifecycle identity and revision;
- closure or termination record;
- contract revision;
- evidence classes affected;
- privacy/data classification;
- applicable retention requirement;
- disposal eligibility;
- legal/security hold status;
- required provenance dependencies.

## Data classes

The system MUST distinguish at least:

- CORE_PROVENANCE;
- AUDIT_EVIDENCE;
- EXECUTION_EVIDENCE;
- GOVERNANCE_RECORD;
- PRIVATE_PAYLOAD;
- DERIVED_ARTIFACT;
- TEMPORARY_CREDENTIAL;
- OPERATIONAL_CACHE.

Each class MUST have an explicit retention/disposal policy.

## Preservation boundary

Core provenance and governance records MUST remain reconstructable for the period required by the governing policy.

Disposal of a payload MUST NOT destroy the metadata necessary to establish:

- that the payload existed;
- its provenance;
- its classification;
- its relevant lifecycle;
- the authorization under which it was handled;
- the disposal decision.

Where cryptographic digests are retained, the digest MUST NOT be represented as proof of payload contents beyond what the digest actually establishes.

## Disposal states

A disposal request MUST use explicit states:

- REQUESTED;
- ELIGIBLE;
- BLOCKED;
- APPROVED;
- EXECUTED;
- FAILED;
- REVOKED;
- VERIFIED.

APPROVED does not mean disposal occurred.

EXECUTED requires execution evidence.

VERIFIED requires evidence that the intended disposal operation completed within scope.

## Eligibility

Disposal MUST be blocked when:

- legal/security hold exists;
- provenance dependency would be destroyed;
- data classification is unknown;
- retention requirement has not expired;
- scope is ambiguous;
- required authorization is missing/revoked;
- conflicting disposal request exists.

Unknown conditions resolve to BLOCKED.

## Disposal authorization

Disposal requires a separate governed authorization identifying:

- exact data/resource;
- exact scope;
- retention basis;
- disposal reason;
- permitted disposal method;
- exclusions;
- executor;
- validity period;
- verification requirements.

No wildcard disposal is permitted.

## Execution and verification

Disposal execution MUST produce separate evidence containing:

- authorization identity;
- resource identity;
- scope;
- execution identity;
- before-state evidence where available;
- result;
- after-state/verification evidence where available.

Disposal execution MUST NOT rewrite historical governance or audit records.

Where complete deletion is impossible, the system MUST record the actual disposal boundary rather than claim complete deletion.

## Privacy boundary

Private payload disposal MAY remove eligible payload data while preserving minimal provenance necessary for audit integrity.

A disposal record MUST NOT unnecessarily reproduce the private payload.

## Recovery and replay

Recovery MUST preserve disposal states, holds, authorizations and evidence.

A failed disposal MUST NOT be treated as completed.

A repeated identical disposal request MAY be idempotent only within the exact authorized scope.

Conflicting replay MUST fail closed.

## Retention-policy changes

Changing a retention policy MUST NOT retroactively authorize disposal without evaluating already-held records under the new governed rule.

Material policy changes require a new policy revision and provenance link.

## Authority separation

Closure != deletion
Retention policy != disposal authorization
Disposal authorization != disposal execution
Disposal execution != disposal verification
Disposal != historical evidence rewrite

No disposal path may mutate Ψ-Core or grant unrelated authority.

## Acceptance gate

E7.84 is satisfied only when implementation and tests demonstrate:

1. explicit data-class separation;
2. retention/disposal separation;
3. hold enforcement;
4. eligibility fail-closed behavior;
5. exact disposal authorization scope;
6. separate execution evidence;
7. verified disposal result;
8. preservation of required provenance;
9. conflicting replay protection;
10. recovery integrity;
11. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.82 — Remediation Result Verification & Governed Closure
- E7.83 — Governed Collaboration Lifecycle Closure & Contract Retirement
- E7.48 — Controlled Execution Evidence / Mutation Receipt

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.84-r1
