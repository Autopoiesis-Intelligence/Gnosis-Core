# E7.37 — Partner Evidence Export & Interoperability Protocol

## Objective

Define deterministic export of authorized partner evidence and reconstruction results to external or partner-controlled machine databases while preserving provenance, revision, integrity and confidentiality without transferring Core authority.

## Export object

For export request x:

X = (export_id, source_revision, subject_refs, evidence_records, reconstruction_context, scope, integrity_manifest)

The export MUST identify the exact source/registry/contract/policy revisions applicable to the exported records.

## Scope

Export content MUST be limited to the requester's effective scope.

Private evidence MUST NOT be included unless explicitly authorized.

An export package MUST distinguish:

- public contract metadata;
- partner-scoped evidence;
- restricted evidence;
- redacted evidence;
- unresolved/conflicted evidence.

## Provenance preservation

Every exported evidence record MUST retain, where applicable:

- evidence identity;
- source revision;
- contract revision;
- policy revision;
- provenance references;
- original event identity;
- correction/revocation references;
- retention/privacy state.

Export MUST NOT flatten distinct historical events into an untraceable final snapshot.

## Integrity manifest

The package MUST provide a deterministic integrity manifest.

Changing exported content, scope, applicable revisions or manifest metadata MUST change the package digest.

Where the project uses content addressing or hash chains, the export SHOULD preserve references into those structures rather than inventing a second authoritative chain.

## Import semantics

An external database receiving the package MUST treat it as imported evidence/context.

Imported evidence is NOT automatically:

- Core state;
- verified truth;
- admission;
- authorization;
- governance state.

The receiving system MAY independently validate and derive local indexes.

## Version and compatibility

The export MUST declare schema/protocol version.

Incompatible versions MUST fail closed or enter an explicitly unsupported state.

A newer package MUST NOT silently overwrite an older package with different provenance.

## Conflict handling

If imported evidence conflicts with local evidence, both provenance chains MUST remain distinguishable.

No arbitrary merge or last-writer-wins behavior is permitted.

The conflict MUST be represented explicitly and, where required, escalated for review/governance.

## Confidentiality

Export MUST enforce recipient scope and approved redaction.

Secrets, credentials and unnecessary private payload MUST NOT be exported.

A redacted record MUST remain distinguishable from an absent record where policy permits.

## Revocation and stale exports

An export MAY later become stale or revoked.

The receiving system MUST preserve the historical fact that the export was issued while preventing the stale/revoked package from silently becoming current.

## Replay/idempotency

Identical source state, scope and export context MAY produce the same export digest.

Conflicting content under an existing export identity MUST fail closed.

## Audit

Export and import events SHOULD participate in the existing audit boundary.

The evidence of export/import MUST identify source, recipient/scope, package digest and applicable revisions without exposing restricted payload unnecessarily.

## Acceptance requirements

Implementation MUST eventually test:

1. deterministic export;
2. scope enforcement;
3. provenance preservation;
4. integrity manifest;
5. schema compatibility;
6. stale/revoked export;
7. conflicting import;
8. duplicate replay;
9. confidential-data exclusion;
10. redaction semantics;
11. cross-partner isolation;
12. export/import audit correlation;
13. interrupted export recovery;
14. imported evidence cannot grant authority;
15. historical provenance remains reconstructable.

## Status

DESIGNED / NOT_IMPLEMENTED.

This contract defines evidence interoperability only. It does not claim that external evidence export/import runtime is implemented.
