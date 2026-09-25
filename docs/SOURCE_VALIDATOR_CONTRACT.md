# Gnozis Source Validator Contract

**Status:** ARCHITECTURAL BASELINE v0.1

Define deterministic validation for Memory Sources before federation registration or update.

## Pipeline

SOURCE.yaml → Schema → Provenance → Relations → References → Revision/Integrity → License metadata → Validation report.

## Required checks

Manifest: stable source_id, supported protocol, declared schemas, repository identity and valid federation status.

Records: schema conformance, required identifiers and resolvable references.

Provenance: required fields and explicit source revision; mutable branch names are not trusted provenance.

Relations: federated relation schema, addressable subject/object, declared predicate and valid verification state.

Integrity: configured digests, duplicate/ambiguous source identities and revision consistency.

Licensing: license metadata and rights information are present before publication.

## Determinism

Identical source content, schemas and validator version should produce the same result.

## Result

The validator reports source_id, validator_version, checked_revision, checks, errors, warnings and `PASS` or `FAIL`.

PASS means protocol compliance for the checked revision. It does not establish scientific truth, commercial quality or suitability.

Structural integrity failures are fail-closed.

## Kernel boundary

Validator PASS does not grant Kernel influence. Kernel consumption still requires Memory Sync and Evidence contracts.
