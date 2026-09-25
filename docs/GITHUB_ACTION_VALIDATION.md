# GitHub Action Validation Contract

**Status:** BOOTSTRAP IMPLEMENTATION v0.1

The repository now defines a GitHub Actions entry point for Memory Source validation.

## Trigger

Validation runs on pull requests and pushes to `main`.

## Permission boundary

The workflow requests `contents: read` only. It must not receive credentials capable of mutating the private Kernel or registering trusted memory by itself.

## Bootstrap result

The current workflow verifies the presence of the source manifest and emits a machine-readable validation artifact. This is deliberately a bootstrap contract, not a claim that the complete schema/provenance/relation validator is already implemented.

## Future validator

The executable validator will replace the bootstrap checks while preserving the same trust boundary and machine-readable result contract.

## Important distinction

CI success means the workflow completed its configured checks. It does not grant Kernel trust, scientific validity or automatic federation authorization.
