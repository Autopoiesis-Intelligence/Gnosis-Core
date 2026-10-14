# Trusted Execution Policy Boundary

Status: CONTRACT / IMPLEMENTATION NOT ACCEPTED

## Purpose

Prevent an execution request from choosing the policy values used to validate itself. A request may carry authorization evidence, but it must not be the authority for the expected policy version or validity-evidence digest.

## Verified defect on integration/replay-provenance-stack

At the audited branch head `d72e855e4e3f2394a596ddf8eaa3dc3e9d714a61`, `gnosis/reflection/trusted_execution_gate.py` passes `validity.policy_version` and `validity.validity_evidence_digest` back to `AuthorizationValidity.require_valid()` as their own expected values. This comparison is self-referential and does not reject a forged policy version. CI run 38524848620 fails `tests/test_trusted_execution_gate_tamper.py::test_tampered_policy_is_rejected_before_consumption` in both Python 3.11 and 3.12 (966 passed / 1 failed in each environment).

The existing `TrustedOwnerIssuer` checks authority root, scope, policy version, evidence presence, approval identity, request provenance, and evolution identity, but it returns only `ExecutionAuthorization`. It does not issue or verify the `AuthorizationValidity` evidence consumed by the gate. The production execution adapter is constructed without an independently configured trusted policy source.

## Required contract

1. **Independent expectation source.** The expected policy version and validity-evidence digest must come from a trusted execution context/provider controlled by the execution composition boundary—not from `ExecutionCommitRequest`, `AuthorizationValidity`, caller-provided keyword arguments, or values copied from the object being checked.
2. **Fail closed.** If the trusted context is missing, incomplete, revoked, stale, or inconsistent with the request, deny before authorization consumption and before Core mutation.
3. **Exact binding.** The validity evidence must bind the authorization ID, policy version, request provenance, exact evolution identity, and any required scope/authority fields. Validation must compare the request against independently established expected values.
4. **One transaction.** Authorization consumption, audit outcome, and Core mutation must retain their existing atomic transaction boundary. Any denial or later failure must leave no authorization-consumption event and no Core mutation.
5. **No fabricated configuration.** Do not hardcode `policy-1`, auto-seed a production policy, or treat a test fixture as a trusted production configuration.
6. **Composition ownership.** Identify the actual production composition root before wiring the provider. If no protected production composition root exists, explicitly keep production execution unavailable/fail-closed; do not disguise a caller-constructible Python object as a cryptographic trust boundary.
7. **Issuer integration.** The trusted issuance path must bind the same policy context and exact authorization/evolution identity to the validity evidence. `TrustedOwnerIssuer` existing in isolation is not evidence of this integration.

## Required regression tests

- A forged policy version is rejected before authorization consumption.
- A forged validity-evidence digest is rejected before authorization consumption.
- A request cannot replace the expected policy/context supplied by the trusted composition boundary.
- Missing trusted context fails closed before consumption and mutation.
- A validity record for another authorization, provenance, evolution, or scope is rejected.
- Revoked/expired authorization is rejected where those lifecycle fields are part of the accepted contract.
- Successful authorized execution uses the trusted context and produces a receipt bound to the exact committed evolution.
- Injected failure after consumption rolls back both consumption/audit effects and Core mutation.
- Tests must exercise the production execution entry point as well as the gate in isolation.

## Acceptance sequence

DESIGN: identify and document the protected composition root and provider contract.
IMPLEMENTED: integrate trusted policy context, issuer, validity evidence, and gate without caller-controlled expected values.
REACHABLE: show the real production execution entry point necessarily traverses that gate and cannot bypass the provider.
RUNTIME: run adversarial and atomicity tests against the actual path.
PERSISTED: verify deny/rollback behavior against the database transaction.
AUDITED: inspect the exact diff for bypasses and configuration injection.
CI_PROVEN: obtain passing CI for the exact resulting commit SHA.

Until every applicable stage is evidenced, trusted execution remains NOT ACCEPTED. Do not merge based on this contract document or on isolated unit-test success.

## Reconciliation update — 2026-10-14

The earlier CI reference above was for the pre-documentation head and is historical. A fresh run was inspected for the current integration PR merge commit generated from head `c5dbdb39bbb7c2497c71825418a2a1755fe56783`:

- CI run: [38527466213](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/actions/runs/38527466213)
- Python 3.11: **966 passed / 1 failed**; Python 3.12 job was cancelled after the failure.
- The same tamper test fails: `test_tampered_policy_is_rejected_before_consumption`.
- Import Graph and CodeQL succeeded for the current PR build. Dependency Review failed separately; it does not negate the specific Python test finding.

A branch-scoped source review found no `TrustedExecutionContext` or trusted policy provider through repository code search. The issuer's only discovered implementation is still the isolated `TrustedOwnerIssuer.issue()` function; it emits `ExecutionAuthorization`, not independently verifiable validity evidence. The adapter still calls the gate without a policy provider.

### Decision

Do **not** patch the failure by hardcoding `policy-1`, copying expected values from the request, or adding an ordinary caller-constructible dataclass and labelling it trusted. Those changes would make the test green without establishing authority provenance.

Next implementation gate: locate or deliberately establish a protected production composition root and its trusted configuration source. If that boundary cannot be established in this repository, the production commit path must remain unavailable/fail-closed while the pure planning/replay paths remain usable. This is a deliberate security constraint, not a passing implementation.

Current status: **DEFECT CONFIRMED ON CURRENT PR BUILD / TRUSTED POLICY SOURCE NOT FOUND / FIX NOT IMPLEMENTED / CI FAIL**.

## Cross-workstream reconciliation — 2026-10-14

A repository-wide reconciliation found that this defect is already tracked in the dedicated security workstream; do not start a duplicate implementation inside the replay-provenance PR:

- [Issue #166 — E8.180 production signed-authorization integration](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/issues/166)
- [Issue #174 — trusted owner evidence before Core commit](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/issues/174)
- [PR #165 — fail closed without independent trusted policy](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/pull/165), still open Draft.
- [PR #167 — signed owner-authorization verifier](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/pull/167), still open Draft.
- [PR #168 — production trust-context interface and adapter integration](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/pull/168), still open Draft.

Inspection of PR #168's current branch shows that `ProductionTrustContext` and a fail-closed adapter path exist there: the adapter requires signed authorization plus a trust context and checks signature/bindings, nonce consumption, and independent validity digest. This is a meaningful implementation step, but the trust context itself is supplied by the caller and the repository has not established who provisions its resolver, policy/scope, clock, and digest resolver from an independently protected trust root. Its own `PRODUCTION_TRUST_CONTEXT_COMPOSITION_GAP.md` records this unresolved boundary. Do not duplicate that interface in this replay PR or mistake a context object for a protected root.

### Current base/CI reconciliation

- Default branch `main` observed at `2a90f28ad75cc63ec3f66c3d9430fe16d95250d9`.
- PR #193 head: `a7162d41d5b906e8e3cb8c868737d9139e31eabc`.
- Comparing PR #193 with current `main`: **32 commits ahead, 2 behind, diverged**; merge base is `13e5b9bd12044d485859f9eda4a6d7fd8d85a9bf`. The PR therefore needs base reconciliation before final acceptance.
- CI run [38527734184](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/actions/runs/38527734184) for the current PR head failed on the same tamper-policy test (Python 3.11); Python 3.12 was cancelled. Import Graph and CodeQL passed; Dependency Review failed separately.
- The mainline head still contains the self-referential gate implementation, while the fail-closed/signed-context work is in unmerged drafts. This explains the known defect's presence in the current base, but does **not** prove the replay PR has no other regressions. A current-main exact-SHA CI comparison is not available from the inspected evidence.

### Scope decision

Keep PR #193 focused on replay/proposal provenance. Treat this document as a warning and cross-reference, not as the implementation of owner authorization. Before merge consideration, reconcile the two-commit base drift and compare the complete failure set against the exact current base. The signed execution work remains governed by Issues #166/#174 and PRs #165/#167/#168. No PR was merged and no production execution acceptance is claimed.
