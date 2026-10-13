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



## Exact-head reconciliation — 2026-10-12 (follow-up)

Exact reviewed PR #168 head: `e1aefaf1f4ebeac4cfd3efef95a9308994629e1a`.
Exact CI run: [38240574621](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/actions/runs/38240574621), run #3607.
PR base SHA remains `381afa025a403a81f32eed4bfa2c44ce01a95540`.

- Python 3.11: **986 passed, 18 warnings**; job PASS.
- Python 3.12: **986 passed, 18 warnings**; job PASS.
- Import Graph: PASS.
- CodeQL: PASS.
- Dependency Review: FAIL. Repository Dependency Graph/configuration is the known issue; this result alone does not establish a vulnerable dependency.
- The passing full-suite result supersedes the earlier exact-head notes above that reported 27 failing tests for older SHAs. Those historical counts remain valid only for their named commits.
- No new base-versus-head test-name comparison was performed for this exact SHA; do not reuse the older comparison as if it were current.

The passing CI closes the current full-suite test blocker for this exact head, but it does **not** close the production trust-composition finding. The repository-local source review still has not identified a deployable production execution entry point that provisions issuer keys/key status, policy/scope, trusted time, and the independent validity-evidence digest resolver. The current package README describes an engineering foundation; the obvious Python entrypoints remain read-only context recovery and read-only reflection.

Next acceptance action: define the intended product boundary explicitly. If this repository is currently a library/foundation rather than a deployable execution service, record that boundary and implement trusted dependency provisioning only in the future application/composition layer. If a deployable service already exists outside this repository, identify its actual source and deployment boundary before wiring the provider. Do not hard-code trust roots or expose trust-context construction to request-controlled inputs.

Updated acceptance status:
- Exact-head full CI: **PASS**.
- Production trust dependency provisioning: **UNRESOLVED**.
- Production composition-root integration: **NOT PROVEN**.
- End-to-end production execution acceptance: **BLOCKED**.


## Exact-head reconciliation — 2026-10-13

Reviewed PR #168 head: `eb014870ef8d207e0a1e6f5986a9e83defc9b16b`.
CI run: [38248625783](https://github.com/Autopoiesis-Intelligence/Gnosis-Core/actions/runs/38248625783).

- Python 3.11: **992 passed, 18 warnings** — PASS.
- Python 3.12: **992 passed, 18 warnings** — PASS.
- Import Graph: PASS.
- CodeQL: PASS.
- Self-Diagnostic: PASS.
- Dependency Review: FAIL; repository Dependency Graph/configuration remains a separate issue and this result alone is not evidence of a vulnerable dependency.

This exact-head result supersedes prior CI counts for older PR #168 commits. It proves the current branch test suite and configured checks above, not deployment/runtime authorization.

### Remaining architecture blocker

The source still does not establish who provisions `ProductionTrustContext` from an independently protected trust root. The adapter accepts a signed authorization and trust context as arguments; the verifier's resolver, policy/scope, trusted clock, and validity-evidence resolver are dependencies, not trust roots. The repo-local search documented here did not identify a production composition root.

Do not hardcode keys/policy, derive trust from caller-controlled request fields, or expose the context as an untrusted public request parameter. Next step is to establish the intended deployment boundary (or explicitly scope Core as a library without a production execution service) and provision trust dependencies there. Until then: signed verifier IMPLEMENTED; trust-context interface IMPLEMENTED; production trust-root provisioning UNRESOLVED; production composition-root integration NOT PROVEN; end-to-end production execution NOT PROVEN.


## Mainline-to-integration boundary cross-check — 2026-10-13

Observed mainline reference: `78f84f6c6ac771478525b547ba467aa773e626b7`.

- Mainline `gnosis/reflection/trusted_execution_gate.py` supplies `validity.policy_version` as its own expected policy and `validity.validity_evidence_digest` as its own expected evidence digest. Those comparisons are self-referential, not independent trust-anchor checks.
- Mainline `gnosis/reflection/execution_adapter.py` calls the gate without a `ProductionTrustContext`; it therefore does not wire signed production authorization into the commit boundary.
- On PR #168's branch, `SQLiteExecutionCommitAdapter.commit` requires both `ProductionAuthorization` and `ProductionTrustContext`, resolves the validity digest through the context, verifies the signature/bindings, consumes the signed nonce transactionally, and passes independent expected values to the gate. This is an integration improvement, but the caller still supplies the context; the context's dependencies are not themselves trust roots.
- A repository code search for `ProductionTrustContext(` on the default branch returned no matches. This search result is bounded evidence, not proof that no external application or unindexed construction exists.

### Decision gate

Do not add a default trust provider inside Core without an identified protected configuration/deployment owner. The current repository evidence supports treating Core as a reusable engineering foundation until the actual application composition boundary is identified. If the product owner intends Core itself to become a deployable execution service, that is a separate product-boundary decision requiring an explicit trust-root provisioning model before implementation.

Status remains: fail-closed signed adapter integration IMPLEMENTED on PR #168; mainline remains vulnerable to self-referential validity checks; production trust-root ownership UNRESOLVED; production execution acceptance BLOCKED. No trust keys or policy values were invented, and no PR was merged.
