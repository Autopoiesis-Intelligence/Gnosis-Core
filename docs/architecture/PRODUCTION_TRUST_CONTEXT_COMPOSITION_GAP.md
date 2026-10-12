# Production Trust Context Composition Gap

Status: OPEN / NOT PROVEN INTEGRATED
Reviewed against: cd485ff4a0752d9a71580abda22867900e0b62ad
PR: https://github.com/Autopoiesis-Intelligence/Gnosis-Core/pull/168

## Finding

The signed owner-authorization verifier and the SQLite execution adapter exist, but source inspection at the reviewed commit did not identify a production composition root that provisions all trust dependencies from an independently protected source.

Relevant boundaries:

- `gnosis/reflection/owner_authorization.py` verifies a signed authorization using a supplied trusted issuer-key resolver. It does not provision the resolver's trust root.
- `gnosis/reflection/production_trust_context.py` requires an issuer-key resolver, authority scope, policy version, trusted clock, and independent validity-evidence digest resolver.
- `gnosis/reflection/execution_adapter.py` fails closed when signed authorization or trust context is missing, but accepts both as arguments from its caller.
- `gnosis/self_learning/execution.py` forwards those arguments; it does not establish their provenance.
- `gnosis/reflection/runtime.py` is a read-only reflection entry point, not a demonstrated production execution composition root.

This is a source-inspection finding, not proof that no external deployment layer exists.

## Required next implementation

1. Identify the actual production entry point and deployment boundary before creating a provider.
2. Define how issuer public keys and key status are provisioned and rotated from a protected trust root.
3. Define the authoritative policy/scope configuration and trusted clock source.
4. Define a durable, independently controlled source for authorization validity evidence digests. Do not derive the expected digest from the request or from the validity record being checked.
5. Construct the trust context only at that trusted boundary. Do not expose a public request parameter that lets a caller choose the trust context.
6. Add integration tests showing that request-controlled key, policy, clock, and digest values cannot become trusted inputs; verify missing or malformed trusted configuration fails closed.
7. Run CI on the exact resulting SHA and inspect runtime wiring before claiming integration.

## Acceptance status

- Signed authorization verification: IMPLEMENTED; focused tests passed in the reviewed CI run.
- One digest resolution per adapter commit: IMPLEMENTED; the focused test passed in the reviewed CI run.
- Production trust dependency provisioning: UNRESOLVED.
- Production composition-root integration: NOT PROVEN.
- End-to-end execution acceptance: BLOCKED.

Do not merge PR #168 based on the focused tests alone. The reviewed CI run has failing Python 3.11 tests; Python 3.12 test jobs were cancelled.

## CI reconciliation — 2026-10-12

Exact reviewed branch head: `a24731af9bd5579cf1ee536b900bcfea76f33186`.
PR #168 base: `381afa025a403a81f32eed4bfa2c44ce01a95540`.

- Python 3.11 on the reviewed head: 27 failed tests.
- Python 3.12: cancelled after the Python 3.11 job failed.
- Graph: PASS.
- CodeQL Python and Actions: PASS.
- Dependency Review: FAIL; repository dependency graph configuration remains a separate issue to investigate.
- The immediately preceding trust-context head's focused test confirmed the digest resolver is called exactly once for a successful commit. That focused result does not establish full-suite or production-runtime acceptance.

The Python 3.11 failure-name comparison with the base CI run (base job 114579119105; head job 114611953200) found 27 shared failing test names, 6 base-only failing names, and zero head-only failing names. This compares test names only; it does not prove causality or that all failures are harmless.

Current failure list is concentrated in legacy execution/authority expectations, endogenous proposal and memory integration, persistence/recovery, and reflection-gate contracts. Do not weaken fail-closed authorization merely to make legacy tests pass. Reconcile the intended contracts and update tests/implementations deliberately.

Acceptance remains BLOCKED until the production trust dependency source is identified and the exact head passes required CI and integration checks.
