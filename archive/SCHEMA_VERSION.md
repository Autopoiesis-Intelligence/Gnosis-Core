# Gnozis Archive Schema Version

Current schema version: **1.0.0**

## Scope

Version 1.0.0 defines the minimum portable record envelope for historical/research material entering Gnozis Archive.

The schema versions the Archive record representation. It does not version Ψ-Core semantics, repository API compatibility, context snapshots, database schema, or research theory itself.

## Required semantic properties

Every durable Archive record must preserve stable record identity, record type, creation/provenance information, source baseline where applicable, content, content integrity when bytes are available, status, and relations to other records when applicable.

## Evidence rule

A record may document a claim, observation, analysis or decision without proving it.

The fields status, verification_status and content_sha256 identify record state and content integrity; they do not establish semantic truth.

## Compatibility

Schema changes must be explicit. A change is breaking when existing records can no longer be interpreted without changing their meaning.

Breaking schema changes require a new major version. Additive optional fields may use a minor version. Non-semantic corrections may use a patch version.

Current version: 1.0.0.