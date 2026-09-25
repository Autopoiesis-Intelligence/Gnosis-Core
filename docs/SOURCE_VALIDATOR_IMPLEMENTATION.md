# Source Validator Implementation

**Version:** 0.1

The repository contains a deterministic, offline bootstrap validator at `tools/validate_memory_source.py`.

## Boundary

The validator reads local repository content only. It does not access the private Kernel, Registry credentials or external services.

## Current checks

- SOURCE.yaml exists;
- required manifest keys exist;
- federation status is recognized;
- machine-readable `validation-result.json` is emitted;
- non-compliance returns a non-zero process exit code.

## Deliberate limitation

This is the first executable layer, not the final protocol validator. Full schema, provenance, relation, reference, integrity and license validation remain subsequent implementation stages.

## CI

The validator can run inside the read-only GitHub Action without granting the workflow mutation authority.
