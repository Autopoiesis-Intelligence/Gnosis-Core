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

## Latest exact-head reconciliation — 2026-10-12

Reviewed branch head: `fad6697931471a0dad039a6ff751898b53e63062`.
CI run: [38212710491](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/actions/runs/38212710491), run #3584.
Base: `381afa025a403a81f32eed4bfa2c44ce01a95540`.

- Python 3.11: **959 passed, 27 failed, 18 warnings**; job failed.
- Python 3.12: cancelled after Python 3.11 failed; no passing result.
- Import Graph: PASS.
- CodeQL: PASS.
- Dependency Review: FAIL (repository Dependency Graph/configuration issue; not evidence by itself of a vulnerable dependency).
- The 27 failures remain concentrated in legacy authority-boundary expectations, endogenous proposal/memory binding, persistence/recovery contracts, and reflection-gate API requirements. The existing base comparison recorded 27 shared failing test names, 6 base-only, and 0 head-only; this is not causal proof.

### Production-entrypoint search

At this exact tree, the only obvious Python entrypoint candidates are `gnosis/context/cli.py` and `gnosis/reflection/runtime.py`. The former emits a read-only context snapshot; the latter performs read-only reflection and persists reflection evidence. The GitHub Actions workflows inspected run tests, diagnostics, observation, or repository watching; none demonstrates production execution composition or trusted-key provisioning.

This narrows the repository-local search but does not prove that an external deployment/composition layer does not exist. Do not manufacture trust configuration or claim production integration. The next implementation step is to identify the intended deployable application boundary (or explicitly define that Gnosis-Core currently has no production execution service) before adding a provider.

## Follow-up: CI on the updated PR head — 2026-10-12

Exact PR head: `2391ab9e5b59d8096e9b1aa952437868d38e745d`.
PR #168 remains OPEN / Draft; base remains `381afa025a403a81f32eed4bfa2c44ce01a95540`.
CI run: [38212892233](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/actions/runs/38212892233).

- Python 3.12: **959 passed, 27 failed, 18 warnings**.
- Python 3.11: cancelled; no result for this head.
- Import Graph: PASS.
- CodeQL: PASS.
- Dependency Review: FAIL, separate repository Dependency Graph/configuration issue.

The failed test names continue to cover four adapter calls that omit the newly required signed authorization/trust context, endogenous proposal/memory integration, persistence/recovery API drift, and reflection-gate authorization arguments. The four adapter tests are contract-conflicting legacy tests: the adapter now intentionally rejects unsigned calls. Do not weaken the fail-closed adapter to satisfy them. Instead, migrate those tests to assert denial without credentials, and retain authorized-path coverage using the signed integration fixtures. This migration must preserve the original candidate-substitution and canonical-head-advance assertions on an authorized request; simply replacing their assertions with a generic denial would reduce coverage.

The latest head therefore remains **CI FAIL / production integration NOT PROVEN**. The source-level entrypoint search does not establish whether the intended product includes a deployable execution service; resolve that product boundary before wiring a trust provider.

