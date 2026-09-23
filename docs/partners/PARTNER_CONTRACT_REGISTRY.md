# Partner Contract Registry

## Purpose

This registry is the machine-readable/documented index of contracts applicable to partner repositories, partner agents and partner contributions.

It is a registry of **contract definitions and revisions**, not an authority store.

## Required separation

Contract definition != contract acceptance
Contract acceptance != partner trust
Partner trust != execution authority

A registry entry MUST NOT grant authority merely by being present.

## Registry record

Each contract record SHOULD contain:

- CONTRACT-ID
- title
- revision
- status
- scope
- applies_to
- dependencies
- source_path
- source_commit
- created_at
- updated_at
- acceptance_requirements
- implementation_status
- verification_status
- supersedes
- superseded_by
- provenance

## Current partner-contract registry

| CONTRACT-ID | Status | Source |
|---|---|---|
| E7.22 | DESIGNED / NOT_IMPLEMENTED | Partner Repository Admission & Identity |
| E7.23 | DESIGNED / NOT_IMPLEMENTED | Partner Contribution Machine-Readable Manifest |
| E7.24 | DESIGNED / NOT_IMPLEMENTED | Partner Contribution Validation & Quarantine |
| E7.25 | DESIGNED / NOT_IMPLEMENTED | Partner Provenance Binding & Immutable Contribution Lineage |
| E7.26 | DESIGNED / NOT_IMPLEMENTED | Partner Admission Runtime Boundary |

## Update rule

Every new partner contract, revision, supersession or acceptance-state change MUST produce a registry update.

The update MUST preserve the previous revision and commit provenance.

No registry update may silently rewrite historical contract state.

## Machine-learning / self-learning use

The registry may be consumed by the Self-Learning Archive as structured contract context.

It MUST be treated as evidence/context, not as an authority root.

The learning system MAY derive:

- contract dependency graphs;
- missing-contract findings;
- stale-contract findings;
- revision conflicts;
- partner-scope mismatches;
- implementation/verification gaps.

It MUST NOT derive execution authority from registry presence.

## Generation and maintenance

The intended future flow is:

Contract proposal
-> Contract review
-> Contract artifact
-> Registry record
-> Implementation
-> Tests / CI evidence
-> Acceptance-state update
-> Revision / supersession

A future registry generator MAY derive records from contract metadata and Git history, but generated output remains subject to verification.

## Integrity requirements

Registry records SHOULD be content-addressable or commit-bound.

A registry entry referring to a contract MUST identify the exact source revision/commit whenever available.

Status claims MUST distinguish:

DESIGNED
IMPLEMENTED
PARTIAL
VERIFIED
UNVERIFIED
REJECTED
SUPERSEDED

## Boundary

This registry does not replace:

- Governance;
- audit log;
- provenance store;
- partner admission;
- verification;
- authorization.

It is the contract knowledge/index layer connecting those systems.

## Status

DOCUMENTED / REGISTRY FOUNDATION

Automatic generation and runtime synchronization are NOT_IMPLEMENTED.
