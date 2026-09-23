# E7.29 — Partner Contract Package & Export Protocol

## Objective

Define the deterministic, provenance-preserving package exported to an invited partner so the partner can consume the applicable contract set without receiving Core authority.

## Package model

For partner p and registry revision r:

K(p,r) = (package_id, registry_revision, contract_set, dependency_closure, evidence_refs, scope, package_digest)

The package MUST identify the exact registry revision and exact contract revisions included.

## Contract set

The package MUST contain only contracts applicable to the recipient's declared/admitted scope.

For every contract:

- CONTRACT-ID;
- contract revision;
- source path;
- source commit/blob;
- status;
- dependencies;
- supersession relation;
- applicable scope;
- verification evidence references where available.

A package MUST NOT silently substitute a newer or older contract revision.

## Dependency closure

If contract c depends on d:

c -> d

then d MUST either:

1. be included in the package; or
2. be explicitly declared as an external dependency with an immutable reference.

An incomplete dependency closure MUST make the package invalid for admission use.

## Evidence references

Evidence references identify supporting CI/runtime/audit evidence.

Evidence references are not copied into authority.

An unavailable or unverifiable evidence reference MUST be marked accordingly and MUST NOT be represented as verified evidence.

## Package integrity

The package MUST have a deterministic representation and digest:

digest(K) = package_digest

Changing:

- contract content;
- contract revision;
- dependency;
- evidence reference;
- scope;
- registry revision

MUST produce a different package digest.

## Recipient binding

The package MAY be bound to a PartnerIdentity and intended scope.

Recipient binding MUST NOT grant authority.

Package recipient binding:

RecipientBinding(p,K) != Authority(p)

## Export/import boundary

Export:

Core Registry
-> Package Generation
-> Integrity/Consistency Check
-> Signed or content-addressed Package
-> Partner

Import:

Partner
-> Package Integrity Check
-> Schema Check
-> Registry/Contract Revision Check
-> Local Consumption

Imported package data MUST remain informational/contractual until independently evaluated by the recipient and the Core admission boundary.

## Staleness

A package MUST be identifiable as stale when its registry revision or any included contract revision is superseded.

Stale packages MUST NOT silently become current.

The recipient MAY request regeneration from the current registry.

## Revocation

A package may be revoked independently of historical packages.

Revocation MUST preserve:

- package identity;
- registry revision;
- package digest;
- recipient binding;
- export event;
- revocation event.

Revoking a package MUST NOT rewrite the contracts from which it was generated.

## No authority transfer

Exporting a package MUST NOT transfer:

- Core write permission;
- execution permission;
- governance permission;
- contract-edit permission;
- admission permission;
- partner-management permission.

Formally:

Export(K,p) -> ContractKnowledge(p)

but not:

Export(K,p) -> Authority(p)

## Replay and idempotency

Identical package generation for the same registry revision, contract set, dependency closure and recipient scope MAY produce the same package identity/digest.

A package with conflicting content under an existing package identity MUST fail closed.

## Acceptance requirements

Implementation MUST eventually test:

1. deterministic package generation;
2. exact registry revision binding;
3. dependency closure;
4. evidence-reference preservation;
5. package digest mismatch;
6. recipient/scope binding;
7. stale package detection;
8. revoked package handling;
9. identical package replay;
10. conflicting package replay;
11. export/import integrity;
12. no authority transfer;
13. recovery after interrupted export;
14. historical package preservation.

## Status

DESIGNED / NOT_IMPLEMENTED.

This contract defines the partner package protocol only. It does not claim that package generation, signing, export or import runtime is currently implemented.
