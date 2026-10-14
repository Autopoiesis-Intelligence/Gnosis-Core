# Production execution composition gap

## Status

**BLOCKED — verifier components exist on draft PR #198; a protected production composition root is not established.**

This document records the implementation boundary. It does not certify production authorization, runtime execution, or CI.

## Current call path on canonical main

At the reviewed main base `2a90f28ad75cc63ec3f66c3d9430fe16d95250d9`:

`gnosis/self_learning/execution.py::execute_approved_core_proposal`
→ `SQLiteExecutionCommitAdapter.commit`
→ `require_trusted_execution`
→ transactional authorization consumption
→ candidate binding and persistence.

The existing call passes only the legacy `ExecutionCommitRequest` and actor to the adapter. It does not create or resolve a protected owner key, authoritative clock, trusted policy, or independent validity-evidence digest.

The storage entry point `gnosis/storage/database.py::connect` initializes SQLite schema and reflection persistence. It is a database connection boundary, not an owner-authority composition root. No protected trust-root composition was identified in the bounded call-site search.

## Components proposed by PR #198

- `owner_authorization.py`: Ed25519 verification for a signed canonical authorization and its exact request bindings.
- `production_trust_context.py`: contract for a key resolver, authority scope, policy version, clock, and independent evidence-digest resolver.
- `execution_adapter.py`: fail-closed commit requiring signed authorization and a trust context.
- `trusted_execution_gate.py`: requires separately supplied expected policy and evidence digest.
- `authorization_consumption.py`: records one-time authorization/nonce consumption in the transaction.

These are necessary building blocks, not proof of a protected composition root. Because the trust context and resolver are currently injectable, the caller could supply untrusted dependencies. An ephemeral test key proves only cryptographic mechanics, not production ownership.

## Required next implementation gate

Before any production commit path is enabled, the application must own a composition boundary that:

1. Loads issuer public keys and key status from a protected, independently administered trust source; callers and request payloads cannot choose or replace it.
2. Provides policy version and authority scope from protected configuration/policy state, not from the request or authorization itself.
3. Provides authoritative time through an explicitly trusted clock; no caller-supplied timestamp.
4. Resolves validity-evidence digests from a durable, independently controlled source and checks the exact authorization ID.
5. Binds the signed authorization to the exact evolution identity, parent-state digest, request provenance, policy, scope, and validity interval.
6. Consumes both authorization ID and nonce atomically with the Core commit; concurrent replay attempts must fail.
7. Exposes no public helper that accepts a caller-created trust context as equivalent to production authority.
8. Has integration tests through the real application entry point, including missing/untrusted key source, policy tampering, digest substitution, expired/revoked key, replay/concurrency, rollback, and successful authorized commit.
9. Has green exact-head CI and runtime evidence before the evidence ladder advances beyond IMPLEMENTED / TESTED.

## Explicit non-goals

- Do not mint a production private key or invent a default trust root in the repository.
- Do not treat an ephemeral test key as production authority.
- Do not derive expected policy or evidence digest from the supplied `AuthorizationValidity` object.
- Do not silently add a local wall clock or caller-provided clock as a trusted source.
- Do not add schema migrations or change runtime storage composition merely to make tests pass.
- Do not mark the authorization system production-ready while the composition root is absent.

## Evidence status

| Layer | Status |
|---|---|
| Design | Defined, with composition gap explicit |
| Verifier implementation | Present on PR #198 draft |
| Reachable from real protected composition root | Not established |
| Runtime end-to-end execution | Not proven |
| Durable trust-root provisioning | Not proven |
| Independent audit | Not complete |
| CI proven | No; exact-head full suite remains red |

## Decision

Keep PR #198 Draft. The next task is to identify the actual application/service boundary that owns the execution request and trusted configuration. If this repository is only a reusable Core library and has no application service, record the external integration contract rather than pretending the library itself can establish production trust.
