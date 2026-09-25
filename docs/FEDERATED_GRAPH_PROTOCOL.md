# Gnozis Federated Graph Protocol

**Status:** ARCHITECTURAL BASELINE v0.1
**Date:** 2026-09-25

A minimal interoperable relation format lets independent Memory Sources publish machine-readable relationships without granting authority over Gnozis or the private Kernel.

## Relation

`subject --predicate--> object`

Required semantics: relation_id, subject, predicate, object, source_id, source_revision, provenance, verification_state and schema_version. Optional content digest and evidence references should be included when available.

Resource references should identify source_id, stable resource_id and revision. A mutable branch name alone is not a trusted identity.

## Predicates

Examples: supports, contradicts, derives_from, depends_on, related_to, implements, validates, cites, contributes_to, supersedes.

A predicate is a claim type, not proof of truth.

## Verification

Relations may be unverified, source_validated, independently_verified, disputed, rejected or withdrawn. An unverified relation must not become trusted merely because another source references it.

## Conflicts

Contradictory relations may coexist. Provenance and verification state are preserved rather than silently collapsing the conflict.

## Security

Publishing a relation grants no access to another repository and no Kernel capability.

## Kernel use

Federated relations remain candidate information until normal source authorization, revision pinning, integrity, schema, provenance and evidence checks succeed.
