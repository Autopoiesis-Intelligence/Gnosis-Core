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


## External integration contract — SEQ 1.22

### Repository-boundary finding

The reviewed canonical-main implementation of `gnosis/self_learning/execution.py::execute_approved_core_proposal` calls the adapter with only `request` and `actor`. PR #198 adds mandatory signed-authorization and trust-context parameters to the adapter, so this existing call path will fail closed until an authorized application integration is deliberately implemented. This is a compatibility/integration blocker, not a reason to weaken the adapter.

A bounded search for application factories and API entrypoints did not identify a production service composition root in this repository. This is a bounded negative finding, not proof that no external service exists. The repository therefore cannot claim to provision owner authority on its own based on current evidence.

### Required host-service interface

An external host that wants to enable production commits must provide a single protected composition operation with the following semantics (names are illustrative; they are not an implemented API):

1. At process/service startup, construct the execution capability from administrator-controlled configuration and protected trust providers. Request payloads must not supply or replace the key resolver, policy source, clock, evidence resolver, database connection policy, or commit adapter.
2. Accept a commit request plus a signed owner authorization as untrusted inputs. Derive the exact evolution identity, parent-state digest, request provenance, scope, and policy expectation from canonical application state and independently controlled policy—not from the authorization itself.
3. Resolve issuer key and revocation/rotation status from a protected source; resolve current time from an explicitly selected trusted clock; resolve the validity-evidence digest from durable independently controlled evidence.
4. Verify signature, key status/validity, scope, policy, identity, parent digest, provenance, and authorization interval before any mutation.
5. Consume authorization ID and nonce and persist the authorized Core transition atomically. If any step fails, roll back both consumption and state mutation. Concurrent duplicate requests must not both commit.
6. Keep the capability out of user-facing serialization and reject request-level dependency overrides. Python object encapsulation alone is not proof against a hostile process with code execution; deployment access controls and configuration ownership must be documented.
7. Test through the actual deployed service entrypoint, including denied requests and rollback/replay/concurrency cases, and retain exact commit SHA, CI run, and runtime evidence.

### Integration decision

Until a real host-service boundary is identified and its trust providers are reviewed, keep the adapter fail-closed and PR #198 Draft. Do not add a fake application factory, default public key, local-clock trust, or test-only production configuration to this library. If no host service exists yet, treat host composition as a separate product implementation gate—not as completed Core functionality.

### SEQ 1.22 evidence

- Canonical-main source inspection: confirmed the current wrapper calls `commit(..., actor=actor)` without the new signed authorization/context inputs.
- Search for common application factory/API entrypoint patterns: no results returned by the bounded code search.
- Status: **EXTERNAL CONTRACT SPECIFIED; PROTECTED HOST COMPOSITION NOT IMPLEMENTED OR PROVEN.**
