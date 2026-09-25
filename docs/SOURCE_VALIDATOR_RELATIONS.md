# Source Validator — Relation Layer

**Version:** 0.5

The validator now checks federated relation records under `relations/`.

Each relation must provide relation identity, subject, predicate, object, source identity, source revision, provenance, verification state and schema version.

Subject and object must be addressable references containing `source_id` and `resource_id`.

Verification state is constrained to the federation protocol states: `unverified`, `source_validated`, `independently_verified`, `disputed`, `rejected`, `withdrawn`.

Malformed or incomplete relations fail closed. This validates protocol structure only; it does not establish the truth of the relation.
