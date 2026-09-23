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
| E7.27 | DESIGNED / NOT_IMPLEMENTED | Partner Replay, Revocation & Contract-State Consistency |
| E7.28 | DESIGNED / NOT_IMPLEMENTED | Partner Contract Registry Runtime Synchronization |
| E7.29 | DESIGNED / NOT_IMPLEMENTED | Partner Contract Package & Export Protocol |
| E7.30 | DESIGNED / NOT_IMPLEMENTED | Partner Contract Acceptance & Capability Negotiation |
| E7.31 | DESIGNED / NOT_IMPLEMENTED | Partner Capability Enforcement & Runtime Scope Boundary |
| E7.32 | DESIGNED / NOT_IMPLEMENTED | Partner Action Audit & Evidence |
| E7.33 | DESIGNED / NOT_IMPLEMENTED | Partner Evidence Review, Dispute & Correction Protocol |
| E7.34 | DESIGNED / NOT_IMPLEMENTED | Partner Evidence Retention & Privacy Boundary |
| E7.35 | DESIGNED / NOT_IMPLEMENTED | Partner Evidence Lifecycle & State Derivation |
| E7.36 | DESIGNED / NOT_IMPLEMENTED | Partner Evidence Query & Reconstruction Protocol |
| E7.37 | DESIGNED / NOT_IMPLEMENTED | Partner Evidence Export & Interoperability Protocol |
| E7.38 | DESIGNED / NOT_IMPLEMENTED | Partner Specialized Core Provisioning & Inbound Trust Boundary |
| E7.39 | DESIGNED / NOT_IMPLEMENTED | Core Minimality & Specialized Knowledge/Learning Layer Boundary |
| E7.40 | DESIGNED / NOT_IMPLEMENTED | Specialized Learning Evolution & Proposal-to-Core Promotion |
| E7.41 | DESIGNED / NOT_IMPLEMENTED | Distributed Clone Learning, Privacy & Network Integration |
| E7.42 | DESIGNED / NOT_IMPLEMENTED | Self-Learning Contract Aggregation, Synthesis & Privacy Boundary |
| E7.43 | IMPLEMENTED / UNVERIFIED | Self-Learning Contract Database Generation & Update Engine |
| E7.44 | IMPLEMENTED / UNVERIFIED | Self-Learning Findings to Contract Proposal Engine |
| E7.45 | IMPLEMENTED / UNVERIFIED | Self-Learning Proposal Validation / Counterexample Gate |
| E7.46 | IMPLEMENTED / UNVERIFIED | Governed Proposal Review / Acceptance Record |
| E7.47 | IMPLEMENTED / UNVERIFIED | Governed Execution / Controlled Contract Application Plan |
| E7.48 | IMPLEMENTED / UNVERIFIED | Controlled Execution Evidence / Mutation Receipt |
| E7.49 | IMPLEMENTED / UNVERIFIED | Append-Only Self-Learning Evidence Ledger |
| E7.50 | IMPLEMENTED / UNVERIFIED | Self-Learning Evidence Replay / Reconstruction |
| E7.51 | IMPLEMENTED / UNVERIFIED | Learning Flow Integrity / Complete Contract Lifecycle |
| E7.52 | IMPLEMENTED / UNVERIFIED | Governed Self-Learning Knowledge Update |
| E7.53 | IMPLEMENTED / UNVERIFIED | Knowledge State Versioning / Lineage |
| E7.54 | IMPLEMENTED / UNVERIFIED | Knowledge Promotion Gate |
| E7.55 | IMPLEMENTED / UNVERIFIED | Controlled Knowledge Integration Record |
| E7.56 | IMPLEMENTED / UNVERIFIED | Protected Core Integration Bridge |
| E7.57 | IMPLEMENTED / UNVERIFIED | Core Mutation Execution Adapter |
| E7.58 | IMPLEMENTED / UNVERIFIED | End-to-End Self-Learning Contract Cycle |
| E7.59 | IMPLEMENTED / UNVERIFIED | Runtime Fail-Closed Execution Boundary |
| E7.60 | IMPLEMENTED / UNVERIFIED | Self-Learning CI Evidence Gate |
| E7.61 | IMPLEMENTED / UNVERIFIED | Self-Learning Candidate Contract Generator |
| E7.62 | PARTIAL / UNVERIFIED | Minimal Specialized Self-Evolving Core |
| E7.63 | PARTIAL / UNVERIFIED | Partner Specialized Core Delivery Package |
| E7.64 | PARTIAL / UNVERIFIED | Partner Training Intake |
| E7.65 | PARTIAL / UNVERIFIED | Partner Training Execution Plan |
| E7.66 | PARTIAL / UNVERIFIED | Training Execution Receipt |
| E7.67 | PARTIAL / UNVERIFIED | Specialized Core Build Record |
| E7.68 | PARTIAL / UNVERIFIED | Specialized Core Validation & Release Gate |

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

## Self-Learning generation engine

The repository now contains the first executable Self-Learning contract database generator:

- `gnosis/self_learning/contract_database.py`;
- `scripts/generate_partner_contract_database.py`;
- `context/SELF_LEARNING_CONTRACT_DATABASE.schema.json`;
- `logs/contracts/partner_contract_database.json` — generated database target;
- `logs/contracts/partner_contract_database.jsonl` — append-only generation/update log;
- `.github/workflows/contract-database.yml` — CI generation and artifact publication.

The generated database is an index-only knowledge artifact and MUST NOT be treated as an authority root.

Registry mutation/automatic status acceptance remains governed and is NOT_IMPLEMENTED.

## Status

PARTIAL / REGISTRY FOUNDATION + SELF-LEARNING GENERATION IMPLEMENTED
