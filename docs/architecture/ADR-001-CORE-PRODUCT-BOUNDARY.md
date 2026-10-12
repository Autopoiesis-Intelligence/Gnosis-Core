# ADR-001: Gnosis-Core product and execution boundary

- Status: **ACCEPTED as the current repository boundary**
- Date: 2026-10-12
- Scope: `Autopoiesis-Intelligence/Gnosis-Core`
- Related: [PR #168](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/pull/168), [Issue #166](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/issues/166), [Production trust context composition gap](PRODUCTION_TRUST_CONTEXT_COMPOSITION_GAP.md)

## Context

The repository README describes Gnosis-Core as the protected engineering foundation / Module Factory from which specialized kernels and user or commercial products may be assembled. It describes reusable state, evolution, verification, authorization, persistence, provenance, and governance mechanisms. It does not define this repository as a deployed user-facing execution service.

Source inspection for E8.181 found signed-authorization verification and a fail-closed SQLite commit adapter. It did not establish a production composition root that provisions issuer keys and key status, trusted policy/scope, trusted time, and independently sourced validity-evidence digests. The existing read-only CLI/reflection entry points do not establish that boundary. This is a repository-local finding; it does not claim that no external application exists.

## Decision

**For the current repository state, Gnosis-Core is a protected reusable library/engineering foundation, not a proven production execution service.**

1. Keep reusable domain mechanisms and the guarded commit adapter in Core.
2. Do not add a pretend production provider, hard-coded issuer keys, invented policy values, or a request-controlled trust context to make the current path appear deployable.
3. Treat production execution as an application/composition-layer responsibility. That layer must obtain key status, policy/scope, time, and validity-evidence provenance from independently protected sources, then construct the trust context internally. Callers must not choose or replace that context through ordinary request data.
4. The application layer may later live in this repository or a separate product repository. That placement is intentionally undecided until a concrete deployable product boundary, operator/deployment model, and trust-root ownership are documented. This ADR does not prescribe a new repository or external service.
5. The adapter remains fail-closed when signed authorization/trust context is absent or invalid. Do not weaken it to satisfy legacy unsigned-call tests.
6. A green test suite establishes only the tested source behavior. It does not establish a production composition root, deployed runtime, independent trust provisioning, or end-to-end production acceptance.

## Consequences

- E8.181 can be reviewed as a reusable security boundary, but it must remain Draft and must not be merged as production-ready solely because CI passes.
- The next implementation is not “invent a trust provider.” It is to define and implement the smallest real application boundary when its deployment and trust inputs are concrete.
- The independent provenance contract for `AuthorizationValidity.validity_evidence_digest` remains a separate blocker and must not be derived from the request or from the record under verification.
- The current product direction remains a governed knowledge/evolution substrate. User-facing memory, connectors, identity, federation, encryption, and autonomous activation are not accepted Core capabilities without their own contracts and runtime evidence.

## Acceptance checklist for a future production execution service

- [ ] Named executable entry point and deployment boundary.
- [ ] Trust-root owner and issuer-key lifecycle documented; unknown, revoked, expired, or mismatched keys fail closed.
- [ ] Policy/scope and trusted-clock sources independently provisioned.
- [ ] Validity-evidence digest source is independent of request and checked record.
- [ ] Request data cannot inject/override any trust dependency.
- [ ] End-to-end tests cover valid authorization, tampering, wrong scope/policy/identity/parent/provenance, expiry, key revocation, replay, missing configuration, and transaction rollback.
- [ ] Exact resulting SHA has required CI passing; runtime wiring and persistence are independently evidenced.
- [ ] Review/audit explicitly distinguishes CI proof from production runtime proof.

## Evidence status at decision time

- README product boundary: documented.
- Repository-local source inspection: reviewed, but not an exhaustive proof about external deployments.
- CI on code/test SHA `e1aefaf1f4ebeac4cfd3efef95a9308994629e1a`: Python 3.11 and 3.12 each 986 passed; Import Graph and CodeQL passed; Dependency Review failed due to the repository Dependency Graph/configuration issue.
- Documentation-only commits after that code/test SHA do not inherit that CI result.
- Production execution service/composition root: **NOT PROVEN**.
