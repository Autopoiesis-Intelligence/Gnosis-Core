# Production Composition Boundary

Status: **DESIGN / BLOCKER — NOT IMPLEMENTED**

Baseline reviewed: `main` at `78f84f6c6ac771478525b547ba467aa773e626b7`.

This document defines the minimum boundary required before signed owner authorization can be treated as production-integrated. It does not claim that the boundary exists.

## Current repository evidence

- `pyproject.toml` declares a Python package but no production `project.scripts` entry point.
- `gnosis/context/cli.py` is a read-only context snapshot command, not a Core mutation application.
- `gnosis/reflection/trusted_execution_gate.py` currently validates `AuthorizationValidity` by passing `validity.policy_version` and `validity.validity_evidence_digest` back as their own expected values. Those comparisons are not independent trust anchors.
- `gnosis/reflection/execution_adapter.py` invokes the gate without a trusted production context.
- `gnosis/reflection/authority.py::issue_execution_authorization` is not a production issuer; it ends in `NotImplementedError`.
- The E5.20 issuer is explicitly test-only. It must remain unavailable as production authority.

These facts establish a missing integration boundary, not that every potential deployment is impossible.

## Required design

The application composition root must be created and owned by the deployment/application layer, outside request-controlled data. It must construct and retain these dependencies:

1. **Issuer key resolver** — public verification keys and active/revoked/rotated status from an independently protected configuration or key-management service.
2. **Trusted policy/scope provider** — the policy version and permitted authority scope selected by deployment policy, not copied from the authorization or commit request.
3. **Trusted clock** — an explicit time source used for authorization and key validity checks.
4. **Validity-evidence resolver** — independently resolves the expected validity evidence digest for an authorization ID.
5. **Commit adapter** — accepts the verified authorization and immutable request, and consumes authorization/nonce plus persists the transition in one SQLite transaction.
6. **Deployment entry point** — creates the composition once, refuses to start in mutation-capable mode when required trust dependencies are missing, and never accepts private keys or trust roots from ordinary request payloads.

## Required trust flow

```text
deployment-controlled trust configuration
  -> application composition root
  -> ProductionTrustContext
  -> verify signed ProductionAuthorization against commit request
  -> bind verified authorization to legacy request/validity records
  -> atomic nonce/authorization consumption + state transition
  -> persisted receipt and audit evidence
```

A request may carry a signed authorization, but it must not supply or override the trust context used to verify that authorization.

## Fail-closed requirements

- Missing resolver, key, policy, scope, trusted time, or validity evidence: deny commit.
- Invalid signature, unknown/revoked/expired key, expired grant, or any request-binding mismatch: deny before durable mutation.
- Replayed authorization ID or nonce: deny.
- Failed persistence: roll back both authorization consumption and state transition.
- `owner_approved=True`, a caller-created dataclass, a valid signature in isolation, or a test fixture is not production authority.
- Never hardcode a private key, owner identity, or policy version to make tests pass.

## Acceptance evidence

Before this boundary can be marked implemented, the PR must include:

- an actual application composition root and documented deployment configuration contract;
- production caller wiring from that root to the existing commit adapter;
- tests proving request data cannot replace trust dependencies;
- end-to-end tests for valid commit, signature tampering, scope/policy/identity/provenance/parent-state mismatch, expiry, key revocation, replay, and transaction rollback;
- exact-head CI results and a base-SHA comparison;
- runtime evidence separately from unit tests and CI.

Until those items exist, the status remains **DESIGN / BLOCKER**. This document is not a substitute for code or runtime proof.
