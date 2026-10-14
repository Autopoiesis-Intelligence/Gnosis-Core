# Evolution Recovery Gate Contract

Status: DESIGN / NOT IMPLEMENTED
Scope: integration between `run_reflection_gate()` and `recover_evolution_audit()`.
Branch context: security/signed-owner-auth-commit-boundary-2026-10-14

## Current observed contract

`run_reflection_gate()` receives instance-recovery authorization, an instance ID, and a timestamp. When the database contains evolution provenance, it calls `recover_evolution_audit(conn)` without a provenance ID, observations, proposed state, or evolution-recovery authorization.

`recover_evolution_audit()` requires a provenance identity for trusted recovery and independently supplied observations and proposed state. It also defaults to rejecting recovery unless authorization is explicitly valid. Therefore, the current call cannot prove evolution recovery and must fail closed. Instance-recovery authorization must not be silently reused as evolution-recovery authority.

## Data-availability finding (repository inspection, 2026-10-15)

The persisted schema was inspected at the current PR head:

- `evolution_provenance` stores identity fields and digests, including `evidence_digest` and `proposed_state_content_id`; it does not store the observation mapping or a reconstructable proposed `State` object.
- `evolution_audit` stores `payload_digest`, not the original audit payload.
- `list_evolution_provenance()` and `list_evolution_audit()` therefore cannot, by themselves, supply the independent replay inputs required by `recover_evolution_audit()`.
- The repository search found no dedicated `EvolutionRecoveryAuthorization` type or `authorize_evolution_recovery` issuance path. The existing `RecoveryAuthorization` is used for instance/partner recovery and must not be silently repurposed.

**Consequence:** the missing inputs are not just an omitted function argument. A trusted producer/source and an evolution-scoped authorization path must be identified or deliberately designed within the existing authority boundary. Do not reconstruct observations or state from digests, and do not add a boolean-to-authority adapter. Until those dependencies exist, the reflection gate must continue to fail closed when evolution provenance is present.

## Existing signed execution boundary (repository inspection, 2026-10-15)

The exact-head inspection also found a separate production-facing signed execution path:

- `gnosis/reflection/owner_authorization.py` verifies Ed25519-signed `ProductionAuthorization` objects against externally provisioned `TrustedIssuerKey` material and checks time, scope, policy, evolution identity, parent-state digest, request provenance, and proposal binding.
- `gnosis/reflection/production_trust_context.py` supplies the trusted key resolver, scope, policy version, clock, and validity-evidence resolver to that verification boundary. Its module contract explicitly says the protected production composition root has not yet been proven in this repository.
- `gnosis/reflection/execution_adapter.py::SQLiteExecutionCommitAdapter.commit()` requires both signed production authorization and a `ProductionTrustContext`, verifies them before mutation, consumes nonce/authorization, checks candidate binding, persists the transition, and checks the resulting state.
- This is an execution-commit boundary, not an evolution-recovery authorization contract. It does not make the original observations or proposed `State` durable replay inputs, and it does not establish that a protected production composition root actually constructs the trust dependencies. Do not treat the existence of these classes as proof that production authority is deployed or that recovery is authorized.

## Production composition-root search (repository inspection, 2026-10-15)

The repository-wide search for `ProductionTrustContext` found its definition and its use as an explicit dependency in `gnosis/reflection/execution_adapter.py` and the bridge function `gnosis/self_learning/execution.py::execute_approved_core_proposal()`. The bridge forwards optional `production_authorization` and `trust_context` arguments and does not create either dependency; omitting them fails closed in the commit adapter. The inspected production bridge therefore is not itself a trusted composition root. Tests exercise the path with a `real_commit_fixture`, but test fixture construction does not prove a deployable trusted issuer-key resolver, trusted clock, validity-evidence resolver, and policy source are wired by production startup.

The current evidence supports a narrow conclusion: signed authorization verification and the mutation adapter exist, but no production construction path for their trust dependencies was found. Do not wire recovery to caller-supplied trust context until its provenance and ownership are established. The next implementation must either identify an existing protected runtime owner for these dependencies or introduce one at the established application boundary with explicit configuration and negative tests for missing/untrusted providers.

## Authorization API mismatch (repository inspection, 2026-10-15)

A further concrete gap is present in `gnosis/evolution/recovery.py::recover_evolution_audit()`: its `authorization_valid` and `authorization_revoked` inputs are plain booleans. The successful recovery unit test supplies `authorization_valid=True` directly. That proves only the function's synthetic branch behavior; it does not prove that a signed authorization was verified, that the caller is trusted, or that the authorization is bound to the selected provenance. The reflection gate currently calls the function without these inputs and therefore fails closed, but the lower-level API can be invoked with a caller assertion.

**Required correction:** do not wire the reflection gate to these booleans. Before trusted recovery can be exposed, replace the boolean assertion with a verified, typed proof produced by the protected authority boundary, bound to the selected provenance identity and evidence scope. Reuse existing signed-owner verification primitives where appropriate, but do not treat a freely constructed data object or a boolean as authority. Until that integration exists, the gate remains fail-closed and positive unit-test coverage must not be reported as production authorization proof.

## Runtime dataflow finding (repository inspection, 2026-10-15)

The exact-head source inspection traced the adjacent production-facing pieces:

- `gnosis/reflection/endogenous_runtime.py::evaluate_candidate_in_sandbox()` receives sandbox execution observations and an evidence digest; `build_endogenous_provenance()` validates and builds `EvidenceProvenance` from those runtime objects. The module explicitly says it does not persist transitions or grant execution authority.
- `gnosis/evolution/transaction.py::persist_evolution_transaction()` atomically stores provenance metadata and an audit record. Its `payload` is reduced to `payload_digest` by the audit-record builder; the original observations and proposed `State` are not made recoverable by this transaction.
- Repository search located the provenance builder in the runtime adapter and persistence calls in the transaction/storage layer, but no production orchestration path connecting the runtime-built provenance and replay inputs to an authorized recovery request.
- Repository-wide reference search found `evaluate_candidate_in_sandbox()` and `build_endogenous_provenance()` used in their definitions and tests, but no production caller of either helper. The restart/replay test explicitly retains the sandbox, candidate, observations, evaluation, and governance objects in memory and passes them to replay; that proves the test path, not that those inputs are available after a real process restart.
- `gnosis/reflection/authority.py::issue_execution_authorization()` still raises `NotImplementedError` after checking approval identity bindings. It is not a usable issuer for `ExecutionAuthorization`. The separate signed `ProductionAuthorization` verifier/commit adapter does not implement evolution-recovery authorization and must not be repurposed implicitly.

**Implementation consequence:** the proven gaps are (1) durable, independently checkable replay inputs, (2) a trusted production composition root for the existing signed execution boundary, and (3) an evolution-recovery-specific authorization and orchestration path. These are distinct. Adding a storage column alone would not establish authority or independent trust. Wiring a caller-supplied boolean into the gate would only disguise the gap.

## Required integration contract

Before implementation, the caller and API must explicitly bind all of the following:

1. **Selection scope** — an explicit provenance ID or a defined, deterministic set of provenance IDs to verify. Never choose an arbitrary first row.
2. **Evidence inputs** — observations and proposed state supplied by an identified trusted source, with digests/content identity checked against the selected persisted record.
3. **Authorization domain** — authorization appropriate to evolution recovery, bound to the selected provenance and evidence scope. Do not convert a boolean, instance authorization, or caller assertion into trusted authority.
4. **Integrity result** — `verified`, `tampered`, and `legacy_unverified` remain distinguishable. Only `verified` may satisfy trusted recovery.
5. **Failure semantics** — missing, ambiguous, mismatched, expired/revoked, or legacy-unverified inputs fail closed with a stable reason. A reflection artifact must not imply that evolution recovery passed when it was not performed.
6. **Compatibility** — legacy rows remain readable, but must not be silently backfilled or promoted to verified without independent evidence and an explicit migration policy.

## Non-goals

- Do not change `provenance_id` or `evolution_identity` semantics to include lifecycle status.
- Do not introduce a second authorization system or bypass the existing trusted-owner / execution-authorization boundary.
- Do not treat a digest stored beside mutable data in the same SQLite database as an external trust anchor.
- Do not make the gate pass merely because recovery was skipped or because no exception was raised.

## Acceptance tests required before implementation is considered complete

- A valid, explicitly selected provenance record with independently supplied matching evidence and valid evolution-recovery authorization can be verified.
- A missing or ambiguous provenance selection fails closed.
- Tampered status, evidence, identity, or audit linkage fails closed.
- A legacy row with no status digest remains `legacy_unverified` and cannot satisfy trusted recovery.
- Instance-recovery authorization alone does not authorize evolution recovery.
- The reflection gate reports success only when every required trust domain has actually passed.
- Existing instance-only gate behavior remains unchanged when no evolution provenance exists.

## Implementation sequence

1. Identify the authoritative producer/source for provenance selection, observations, and proposed state.
2. Identify the existing authorization type and issuance path suitable for this exact evolution-recovery scope; if none exists, document the gap rather than inventing authority.
3. Define the narrowest typed input contract and stable failure reasons.
4. Implement the binding and tests together.
5. Validate exact-head CI, Import Graph, CodeQL, and Dependency Review separately. Do not call the overall check set green while any required check fails.

## Evidence note

This document records a design constraint, not an implementation claim. At the time of writing, the integration gap is observed in `gnosis/reflection/gate.py`, `gnosis/evolution/recovery.py`, `gnosis/reflection/endogenous_runtime.py`, `gnosis/evolution/transaction.py`, and `gnosis/reflection/authority.py`. No runtime or CI proof is implied by this document.
