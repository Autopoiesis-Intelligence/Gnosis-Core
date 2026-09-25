# Gnozis Memory Synchronization & Kernel Consumption Contract

**Status:** ARCHITECTURAL BASELINE v0.1
**Date:** 2026-09-25

## Purpose

Define the safe path by which the private Kernel discovers, synchronizes and evaluates external Memory Sources.

Synchronization is retrieval. It is not trust and it is not consumption.

## Separation of concerns

DISCOVERY → REGISTRY → RETRIEVAL → INTEGRITY CHECK → SCHEMA VALIDATION → PROVENANCE VALIDATION → EVIDENCE EVALUATION → KERNEL CONSUMPTION

No stage may silently imply the next stage.

## Pull model

The default synchronization mode is pull. Kernel-side integration requests a registered source revision without granting the source write access to Kernel state.

## Pinning

A synchronization request should identify source_id, revision identifier, content digest, schema version and protocol version. Mutable branch heads are discovery references, not trusted consumption references.

## Integrity and validation

Digest mismatch, invalid schema, missing provenance, incompatible protocol, revoked source or unauthorized operation are fail-closed conditions.

## Consumption

Only records satisfying Kernel consumption policy may influence Kernel processes. Consumption records should preserve source_id, revision, content digest, record identifiers, validation results, evidence state, policy version and event identifier.

## Source updates

A newer source revision is a new synchronization candidate. It does not automatically replace a previously consumed revision.

## No external mutation

A Memory Source cannot mutate Kernel state, trigger an evolution commit, modify Kernel policy, grant itself permissions or change its Registry authorization.

## Relationship to evolution

Kernel consumption supplies information/evidence to existing Kernel contracts. It does not bypass Candidate → Test → Select → Evolve → Verify → Commit.

External memory is therefore an input to the system rather than an external authority over the system.
