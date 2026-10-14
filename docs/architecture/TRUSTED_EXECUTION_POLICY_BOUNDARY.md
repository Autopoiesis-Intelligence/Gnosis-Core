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
