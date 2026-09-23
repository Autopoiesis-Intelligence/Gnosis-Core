# E7.43 — Self-Learning Contract Database Generation & Update Engine

## Objective

Implement the first executable Self-Learning contract-knowledge index that discovers partner contracts from repository artifacts, compares them with the partner registry, detects deterministic drift, and writes a machine-readable database plus an append-only generation/update log.

## Authority boundary

The generated database is an index/knowledge artifact.

ContractDatabase != Governance
ContractDatabase != Authorization
ContractDatabase != Verification
ContractDatabase != CoreState

Generated output MUST NOT grant capabilities or mutate Core state.

## Inputs

The engine consumes:

- contract artifacts under docs/;
- the partner contract registry;
- contract headings/statuses;
- explicit contract references;
- optional source revision supplied by the caller.

Code, tests and Git history remain authoritative for implementation claims.

## Deterministic database

For each discovered contract the engine records:

- contract_id;
- title;
- status;
- source_path;
- SHA-256 source_digest;
- referenced contract dependencies;
- provenance.

Records and findings are sorted deterministically.

The database MUST remain reproducible for equivalent repository contents. Generation timestamps belong to the update log, not the semantic contract ordering.

## Drift findings

The engine MUST detect:

- registry entry missing for an artifact;
- registry entry without an artifact;
- registry status differing from artifact status;
- referenced contract missing;
- dependency graph gaps.

Findings MUST be preserved in the generated database and MUST NOT silently repair source artifacts.

## Partner database output

Default generated database:

logs/contracts/partner_contract_database.json

The output declares:

authority = index_only

and:

provenance = self-learning-contract-database

## Update log

Every generation MUST append an event to:

logs/contracts/partner_contract_database.jsonl

Each event records:

- event type;
- UTC generation time;
- source revision;
- generated database digest;
- contract count;
- finding count;
- output path;
- authority classification.

The log is evidence of generation activity, not an authority source.

## Atomicity

Database replacement MUST be atomic within the filesystem boundary: write a temporary sibling and replace the target only after serialization succeeds.

A failed serialization MUST NOT leave a partially written database at the target path.

## Privacy

The initial database stores contract metadata and source digests, not private user/partner payloads.

Private knowledge MUST NOT be copied into the partner contract database by this engine.

## Self-Learning boundary

The engine provides the machine-maintained contract knowledge substrate for future Self-Learning operations:

Observe -> Retrieve -> Compare -> Find -> Hypothesize -> Propose -> Validate -> Govern -> Record -> Learn

This implementation covers the Retrieve/Compare/Find/Record substrate. It does not autonomously accept proposals or alter Core.

## Acceptance evidence

Required tests cover:

1. deterministic repeated generation;
2. dependency extraction;
3. missing registry entry;
4. missing artifact;
5. status drift;
6. missing dependency;
7. atomic output replacement;
8. generation log append;
9. source digest generation;
10. index-only authority marker;
11. source-revision propagation;
12. no Core mutation.

## Status

IMPLEMENTED / UNVERIFIED.

Implementation exists in:

- gnosis/self_learning/contract_database.py
- gnosis/self_learning/__init__.py
- context/SELF_LEARNING_CONTRACT_DATABASE.schema.json
- tests/test_self_learning_contract_database.py

Runtime/CI verification remains separate evidence and MUST NOT be inferred from source presence.
