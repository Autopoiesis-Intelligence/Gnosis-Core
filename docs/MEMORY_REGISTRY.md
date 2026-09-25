# Gnozis Memory Registry

**Status:** ARCHITECTURAL BASELINE v0.1
**Date:** 2026-09-25

## Purpose

The Memory Registry is the Kernel-side index of authorized Memory Sources.

It describes which sources exist, what domains they represent, which revisions are known, what permissions are granted, and whether a source is currently usable.

The Registry is metadata and policy. It is not a copy of every repository.

## Source lifecycle

```
DISCOVERED
  -> REGISTERED
  -> AUTHORIZED
  -> SYNCING
  -> VERIFIED
  -> ACTIVE

Failure or policy change may move a source to:

QUARANTINED / REVOKED / DISABLED
```

## Required source metadata

Each registry entry SHOULD identify:

- source_id;
- owner;
- domain;
- repository locator;
- protocol version;
- contract version;
- declared license;
- authorization policy;
- permissions;
- synchronization policy;
- latest known revision;
- content digest;
- schema version;
- verification state;
- provenance policy;
- last successful synchronization;
- revocation state.

## Trust model

Registration does not mean that every record is trusted.

The Registry authorizes a source to participate in the Memory Source Protocol. Individual revisions and records remain subject to validation and Kernel evaluation.

## Permission model

Permissions are scoped per source and may include:

- READ;
- ANNOTATE;
- PROPOSE;
- PUBLISH.

DELETE and history rewriting are prohibited by default.

## Revision pinning

The Registry MUST support immutable revision references.

A branch or tag alone is not a sufficient trusted reference.

A usable revision record should include:

```
source_id
commit/revision
content_digest
schema_version
verification_state
```

## Revocation

A source may be revoked without deleting its historical records.

Revocation prevents new consumption according to policy while preserving auditability and provenance.

## Registry invariants

1. Unknown sources cannot influence trusted Kernel state.
2. Registration cannot bypass provenance validation.
3. A mutable reference cannot substitute for a pinned revision.
4. Revocation cannot silently erase historical provenance.
5. Source permissions cannot exceed the Memory Source Contract.
6. Registry metadata cannot itself be treated as domain evidence.

## Relationship to Kernel

The Registry is the boundary between the private Kernel and the external Memory Network:

```
Memory Network
      |
      v
Memory Registry
      |
      v
Memory Source Protocol
      |
      v
Validation / Verification
      |
      v
Kernel consumption
```

The Registry therefore provides discoverability and authorization, while verification determines whether a particular revision may influence the Kernel.
