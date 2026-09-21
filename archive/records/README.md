# Archive Records

Records are the atomic historical units of Gnozis Archive.

## Record envelope

Each record contains, at minimum: schema_version, record_id, record_type, created_at, producer, baseline, status, verification_status, content, content_sha256, and provenance.

## Record types

Initial types: research, reverse_analysis, evidence, snapshot, summary, decision, audit.

Additional types require an explicit schema update.

## Provenance

The record must preserve enough information to identify where the material originated, who/what produced it, which repository baseline it describes when applicable, what transformation was applied, and what verification actually occurred.

## Migration rule

Do not migrate a historical item by rewriting its meaning.

If the source contains uncertainty, rejection, incomplete evidence or conflicting interpretations, the Archive record must preserve that state.

A summary may reference raw records but must not silently replace them.

## Core boundary

Archive records are historical information. They do not directly authorize Core mutation, governance activation, capability grants, execution, rollback, or authority issuance.