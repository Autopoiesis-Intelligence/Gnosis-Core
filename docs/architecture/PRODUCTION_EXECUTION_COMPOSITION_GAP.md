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

## SEQ 1.38 — bridge proposal-to-commit binding gap (2026-10-14)

A fresh read of the PR branch at `security/signed-owner-auth-commit-boundary-2026-10-14` found a second, narrower integration gap in `gnosis/self_learning/execution.py`:

- `execute_approved_core_proposal()` calls `bind_core_proposal(proposal, request)`, which validates that the proposal is marked `APPROVED`, that its `mutation_id` matches its own immutable bridge fields, and that the request has an evolution identity.
- `bind_core_proposal()` returns a `BoundCoreExecution` containing the proposal ID, evolution identity, and a binding digest.
- The returned binding is currently discarded by the caller. The binding digest is not passed to `SQLiteExecutionCommitAdapter.commit()`, and `ProductionAuthorization` does not carry an explicit bridge-proposal binding field.
- The signed authorization does bind the commit request's evolution identity and provenance fields. However, the reviewed bridge does not establish that the particular approved `CoreMutationProposal` is the proposal represented by that signed commit request.

**Status: IMPLEMENTED bridge validation; proposal-to-commit authorization binding NOT ESTABLISHED.** This is a code-path finding, not proof of an exploitable production route: the protected production composition root is still not established.

### Required correction

1. Define a canonical proposal-binding field in the signed authorization contract (or a rigorously equivalent signed request identity); it must cover `mutation_id`, `integration_id`, `version_id`, `target`, and `action`.
2. Verify that binding against the exact approved proposal at the protected commit boundary, before nonce consumption or persistence.
3. Fail closed when a signed authorization is paired with a different approved proposal, even if both proposals are individually valid and the request evolution identity is otherwise valid.
4. Add adversarial tests for proposal A + authorization for proposal B, modified target/action/version, and the matching positive case. Test through the real bridge and adapter, not only a monkeypatched forwarding stub.
5. Keep the signed schema change on the draft branch until the issuer/consumer contract and migration implications are explicit; do not infer that old signatures remain compatible.

No production readiness or runtime execution claim follows from this finding. PR #198 remains Draft and must not be merged until this gap, protected trust composition, end-to-end tests, and exact-head CI are addressed.



## SEQ 1.40 — proposal-binding implementation and exact-head CI (2026-10-14)

At branch HEAD `4e5ab97ed4d7a5602569e7e465a73458c22b4a27`, the bridge proposal-to-commit binding correction is implemented in the Draft branch:

- `ProductionAuthorization` includes `proposal_binding_digest` in its canonical signed payload and authorization identity.
- `verify_production_authorization()` requires an independently supplied `expected_proposal_binding_digest` and rejects mismatch.
- `execute_approved_core_proposal()` retains the `BoundCoreExecution` result and forwards its digest to the adapter.
- `SQLiteExecutionCommitAdapter.commit()` fails closed if the expected binding is missing.
- A negative verifier test rejects an authorization bound to a different proposal. Direct adapter fixtures and replay/substitution tests pass the expected binding explicitly.

### Exact-head CI evidence

- CI run [38556270933](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/actions/runs/38556270933), SHA `4e5ab97ed4d7a5602569e7e465a73458c22b4a27`: **952 passed, 23 failed, 18 warnings**. Python 3.11 and 3.12 both failed with the same 23 failure identifiers.
- The prior new replay-test omission is no longer among the failures. No new failure in the proposal-binding verifier/adapter tests appears in the reported failing-test list; this is useful regression evidence but not a green CI result.
- Import Graph run [38556270959](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/actions/runs/38556270959): PASS.
- CodeQL run [38556271099](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/actions/runs/38556271099): PASS.
- Self-Diagnostic run [38556264785](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/actions/runs/38556264785): FAIL before diagnostic generation, with six persistence-test failures; this run did not produce the diagnostic artifact.
- Dependency Review run [38556270919](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/actions/runs/38556270919): FAIL; repository dependency-graph/configuration limitation remains to be separately classified.

The 23 full-suite failures cluster in endogenous proposal/candidate binding, evolution-memory and persisted-chain contracts, persistence/recovery behavior, and reflection-gate call sites. Do not claim these are all baseline failures without a matching-base comparison. This run proves the suite remains red, not that the security patch is production-ready.

### Updated evidence status

| Layer | Status |
|---|---|
| Design | Defined; host-composition gap remains explicit |
| Proposal binding implementation | Present on Draft branch |
| Targeted negative proposal-binding test | Present; not listed among exact-head failures |
| Exact-head full CI | FAIL — 952 passed, 23 failed |
| Protected production composition | Not established |
| Runtime end-to-end execution | Not proven |
| Durable trust-root provisioning | Not proven |
| Production readiness | Not proven |

Decision: keep PR #198 Draft. Next, compare the 23 failing test identifiers against a fresh CI run on the PR base SHA, and inspect the real protected host boundary before attempting runtime claims. Do not broaden this security PR into unrelated persistence/endogenous-runtime repairs without an evidence-based dependency reason.
