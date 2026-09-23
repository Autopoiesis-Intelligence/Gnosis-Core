# E7.22 — Partner Repository Admission and Identity Contract

## Objective

Define controlled admission of an external partner repository into the Gnozis learning environment.

## Admission lifecycle

PROPOSED
-> IDENTITY_ASSIGNED
-> METADATA_VALIDATED
-> SCOPE_DECLARED
-> PROVENANCE_BASELINED
-> SECURITY_AUDITED
-> QUARANTINED
-> ADMITTED
-> ACTIVE_SOURCE

Failure states:

REJECTED, SUSPENDED, REVOKED.

Admission MUST NOT imply trust or execution authority.

## Partner identity

Each partner repository MUST receive an immutable PartnerIdentity distinct from:

- human identity;
- agent identity;
- repository URL/name;
- execution authority;
- organization role.

Repository forks or renamed mirrors MUST NOT silently inherit authority.

## Scope declaration

Admission records MUST define:

- allowed contribution classes;
- allowed domains;
- permitted learning targets;
- prohibited data/classes;
- revision policy;
- retention policy;
- revocation mechanism.

Undeclared capabilities are denied by default.

## Baseline provenance

The admitted baseline MUST identify:

- repository revision;
- contribution manifest;
- declared authorship/ownership metadata;
- audit result;
- admission decision;
- admission contract revision.

Subsequent revisions are new evidence nodes.

## Quarantine

Before admission, partner material remains isolated from Core learning promotion.

An admission decision is itself immutable and auditable.

## Revocation

Revocation blocks future ingestion/promotion according to policy and triggers dependency impact analysis for previously derived learning artifacts.

Revocation does not erase historical provenance.

## No authority inheritance

PartnerIdentity, reputation, admission status or successful historical contributions MUST NOT automatically grant execution authority.

## Acceptance

Tests MUST cover identity collision, fork/rename, scope escalation, revision substitution, admission bypass, revoked partner, historical provenance preservation and restart/recovery.

Status: DESIGNED / NOT_IMPLEMENTED.
