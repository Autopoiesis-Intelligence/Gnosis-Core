# E7.86 — External Auditor Verification & Attestation Boundary Contract

## Objective

Define the boundary between external verification of an audit package and any attestation or conclusion derived from that package.

An auditor may verify package integrity and documented evidence relationships, but verification MUST NOT silently become authority over the source system, Ψ-Core, governance, private data or future actions.

## Preconditions

An auditor verification request MUST reference:

- exact audit package identity/digest;
- package generation revision;
- evidence manifest;
- recipient/audience identity;
- verification scope;
- verification method;
- applicable audit/attestation policy revision.

## Verification states

Verification MUST use explicit states:

- REQUESTED;
- IN_PROGRESS;
- VERIFIED;
- FAILED;
- PARTIAL;
- UNKNOWN;
- REJECTED;
- SUPERSEDED.

VERIFIED means the declared verification criteria were satisfied for the stated scope only.

## Verification scope

The verifier MUST distinguish:

1. package integrity;
2. provenance linkage;
3. evidence completeness relative to the declared manifest;
4. consistency of recorded state transitions;
5. authenticity of signatures/digests where applicable;
6. substantive claims supported by the included evidence.

Verification of one layer MUST NOT be represented as verification of another.

## Attestation states

An attestation MUST use explicit states:

- DRAFT;
- ISSUED;
- QUALIFIED;
- WITHDRAWN;
- SUPERSEDED;
- EXPIRED.

An attestation MUST declare:

- exact subject;
- exact package identity/digest;
- verification scope;
- verification criteria;
- limitations;
- verifier identity;
- issuance revision;
- applicable period.

QUALIFIED MUST identify the qualification/limitation rather than conceal it.

## No authority transfer

External verification or attestation MUST NOT:

- grant repository permissions;
- grant partner capabilities;
- authorize execution;
- authorize disclosure;
- mutate Ψ-Core;
- modify governance records;
- create standing authority.

Any requested action requires its own governed contract path.

## Evidence limitations

The verifier MUST record when:

- evidence is incomplete;
- source payload was intentionally excluded;
- redaction limits interpretation;
- cryptographic identity is unavailable;
- external state cannot be independently observed;
- the package only establishes recorded provenance rather than underlying truth.

The verifier MUST NOT claim stronger certainty than the evidence supports.

## Independence and conflict

If the verifier identifies conflicting evidence:

- preserve the conflict;
- identify the conflicting artifacts;
- mark the affected verification scope PARTIAL, FAILED or UNKNOWN as appropriate;
- do not silently select one record without recording the basis.

A verifier may issue a qualified attestation where policy permits, but the qualification MUST remain explicit.

## Revocation and supersession

An attestation MAY be withdrawn or superseded.

Withdrawal MUST preserve the historical fact that the attestation existed.

A superseding attestation MUST reference the prior attestation and identify material changes.

Underlying package/evidence changes MUST NOT mutate an existing attestation.

## Privacy boundary

Verification MUST operate on the minimum evidence necessary.

Auditor access to a package MUST NOT imply access to private source payloads.

Requests for additional private evidence require separate authorization.

## Replay and recovery

Verification records and attestations MUST survive restart/recovery.

Identical verification requests MAY be idempotent when package, scope, criteria and verifier identity are identical.

Conflicting replay MUST fail closed.

## Acceptance gate

E7.86 is satisfied only when implementation and tests demonstrate:

1. explicit verification state machine;
2. layered verification scope;
3. exact package binding;
4. explicit evidence limitations;
5. separate attestation state machine;
6. no authority transfer;
7. conflict preservation;
8. withdrawal/supersession without history rewrite;
9. privacy enforcement;
10. recovery/replay integrity;
11. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.85 — Collaboration Evidence Export & External Audit Package
- E7.82 — Remediation Result Verification & Governed Closure
- E7.84 — Lifecycle Retention, Evidence Preservation & Controlled Data Disposal

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.86-r1
