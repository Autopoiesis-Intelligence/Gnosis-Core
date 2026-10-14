# Current Execution Trust Boundary

Status: **BLOCKED — trust-root ownership and production composition are not established**

Reviewed default branch: `main`
Reviewed source SHA: `2a90f28ad75cc63ec3f66c3d9430fe16d95250d9`
Review date: 2026-10-14

## Decision

Do not create a default trust provider or hard-code issuer keys, policy, scope, time, or validity evidence in Gnosis-Core until the protected configuration owner and deployment boundary are identified.

Current repository evidence describes Gnosis-Core as an engineering foundation. It does not establish a production execution service that provisions the required trust dependencies. Treat Core as a reusable foundation for this work unless the product owner explicitly defines a deployable execution service and its trust-root owner.

## Confirmed source findings on the reviewed main SHA

- `gnosis/reflection/trusted_execution_gate.py` compares the authorization validity object's policy version and evidence digest against values taken from that same object. These comparisons are self-referential and do not independently establish trust.
- `gnosis/reflection/execution_adapter.py` invokes the gate without an independently provisioned trust context or signed production authorization.
- `gnosis/self_learning/execution.py` calls `SQLiteExecutionCommitAdapter().commit(..., actor=actor)` without forwarding a signed authorization or trust context.
- PR #168 contains a signed authorization verifier and a `ProductionTrustContext` interface, but it is a separate Draft branch. Its adapter accepts the context from the caller; the context's key resolver, policy/scope, clock and evidence-digest resolver are dependencies, not the trust root.
- The self-learning entry point on that branch does not demonstrate forwarding those required arguments. Therefore end-to-end reachability remains unproven.

## Required implementation order

1. Identify the actual deployable application/composition boundary and the party or protected mechanism that owns trust-root provisioning.
2. Specify issuer key identity, key status and rotation; authoritative policy and scope; trusted time; and an independently controlled, durable validity-evidence digest source.
3. Construct the trust context only at that protected boundary. Request-controlled values must not choose or replace trust dependencies.
4. Wire the signed authorization path through the existing commit adapter and the intended production entry point. Preserve transactionally atomic nonce consumption and denial-before-mutation.
5. Test forged/missing keys, policy, time and evidence; authorization/request binding mismatches; replay; and unchanged durable state after denial.
6. Run required CI on the exact resulting SHA and verify the reachable runtime path before claiming production integration.

## Evidence status

| Claim | Status |
|---|---|
| Self-referential validity check exists on reviewed main | Confirmed by source inspection |
| Signed authorization verifier exists on PR #168 | Confirmed on that branch only |
| Trust-root provisioning is implemented in this repository | Not established |
| Signed path is reachable through the intended production entry point | Not established |
| End-to-end production execution is accepted | Blocked |

This document records source-level findings, not runtime proof. Recheck the default-branch SHA before using these findings as current evidence. No PR is authorized to merge solely because focused tests pass.
