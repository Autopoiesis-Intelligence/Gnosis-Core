# Source Validator — Schema Layer

**Version:** 0.3

The validator now checks that a Memory Source declares a local `schema/` directory containing at least one `*.schema.yaml` or `*.schema.yml` file.

Each discovered schema must be non-empty and declare both `version:` and `required:` fields.

This is intentionally a structural schema-presence check, not yet a complete YAML Schema validator. It establishes the next deterministic trust boundary without silently treating malformed or absent schema declarations as valid.

The validator remains offline and has no Kernel or Registry credentials.
