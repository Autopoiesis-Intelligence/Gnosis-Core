# E7.44 — Self-Learning Findings to Contract Proposal Engine

## Objective
Transform deterministic Self-Learning findings into machine-readable, bounded contract proposals without granting the Self-Learning layer authority to accept, activate, or silently rewrite contracts.

## Pipeline
Findings -> Normalize -> Deduplicate -> Classify -> Propose -> Validate -> Govern -> Record

The implementation covers Normalize/Deduplicate/Classify/Propose/Record.

## Boundary
A proposal contains proposal_id, contract_id, proposal_type, finding, rationale, provenance, proposed_change and status.

Proposal status begins as PROPOSED. The engine MUST NOT mutate contract files, Core invariants, permissions, partner access, or runtime state.

## Determinism
Equivalent finding input produces equivalent proposal content and SHA-256 proposal identifier.

## Privacy
Proposal generation operates on contract metadata/findings and MUST NOT copy private user or partner payloads.

## Governance
A generated proposal is evidence for review, not an accepted contract.

## Status
IMPLEMENTED / UNVERIFIED.

Implementation:
- gnosis/self_learning/proposals.py
- tests/test_self_learning_proposals.py
