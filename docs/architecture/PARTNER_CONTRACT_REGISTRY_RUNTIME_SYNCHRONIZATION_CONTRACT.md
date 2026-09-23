# E7.28 — Partner Contract Registry Runtime Synchronization Contract

## Objective

Define the machine-maintained contract registry as a provenance-preserving index synchronized with contract artifacts, implementation state and verification evidence.

## Registry authority boundary

The registry is an index, not an authority root.

RegistryEntry != Permission
RegistryEntry != Trust
RegistryEntry != Verification
RegistryEntry != Admission

A registry record MUST never grant a partner or runtime component a capability merely because the record exists.

## Canonical sources

For each contract, the registry MUST reference:

1. contract artifact path;
2. exact source commit/blob revision;
3. contract ID and revision;
4. dependency identifiers;
5. implementation status;
6. verification status;
7. supersession relation where applicable.

The contract artifact and Git history remain authoritative for the existence and revision of the contract.

## Synchronization event

A registry update is required when any of the following occurs:

- contract creation;
- contract revision;
- contract supersession;
- implementation status change;
- verification status change;
- acceptance/rejection;
- dependency change.

Each synchronization MUST create an auditable update.

## State derivation

Registry status MUST distinguish at least:

DESIGNED
IMPLEMENTED
PARTIAL
VERIFIED
UNVERIFIED
REJECTED
SUPERSEDED

Documentation alone MUST NOT promote a contract to VERIFIED.

Source presence alone MUST NOT promote a contract to VERIFIED.

Tests existing in the repository MUST NOT be represented as executed evidence unless runtime/CI evidence exists.

## Drift detection

A synchronizer MUST be able to detect at least:

- registry entry points to a missing artifact;
- recorded commit differs from current contract revision;
- contract exists but registry entry is absent;
- registry reports a status unsupported by available evidence;
- supersession relation is inconsistent;
- dependency references are missing or unresolved.

Detected drift MUST produce a finding/event and MUST NOT silently repair historical records.

## Update model

Preferred flow:

Contract artifact
-> metadata extraction
-> registry candidate
-> consistency checks
-> registry update
-> audit event

A failed consistency check MUST prevent an authoritative registry promotion.

## History

Registry updates MUST be append-aware.

The current registry may expose the latest state, but prior registry states MUST remain recoverable from Git history and/or an explicit registry event log.

No update may erase the fact that an earlier contract revision existed.

## Partner use

The registry MAY be exported to partner repositories as a machine-readable contract package.

An exported package MUST identify:

- registry revision;
- contract revisions;
- source commits;
- dependencies;
- status;
- verification evidence references;
- applicable scope.

A partner MUST NOT treat an exported registry package as permission to modify Core or bypass admission.

## Existing persistence boundary

Where runtime synchronization is implemented, registry events SHOULD use the existing append-only audit and transactional persistence boundary rather than introducing an independent authority database.

The registry MUST remain logically separate from Core state.

## Acceptance requirements

Implementation MUST eventually test:

1. creation synchronization;
2. revision synchronization;
3. missing-contract detection;
4. stale-commit detection;
5. undocumented status promotion rejection;
6. supersession consistency;
7. dependency integrity;
8. registry recovery after restart;
9. append-only history;
10. export/import provenance preservation;
11. no authority escalation;
12. atomicity of registry update and its audit event where persistence is used.

## Status

DESIGNED / NOT_IMPLEMENTED.

This contract defines the synchronization boundary; it does not claim that automatic registry generation or runtime synchronization is currently implemented.
