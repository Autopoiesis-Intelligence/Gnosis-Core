# Gnosis-Core Working-State Recovery — 2026-10-12

Status: RECONCILED AGAINST LIVE GITHUB METADATA; code/runtime state not fully accepted.
Purpose: restore a durable handoff after repeated conversation/tool failures. This document records evidence and next actions; it does not certify product readiness.

## 1. Canonical repository and observed refs

- Repository: `Autopoiesis-Intelligence/Gnosis-Core`
- Default branch: `main`
- Exact main HEAD observed on 2026-10-12: `00648d14106de03e194c58d90790d2fe202670a4`
- Main HEAD commit: `chore: refresh current partner contract block`
- The current main HEAD has no workflow runs returned by the commit-workflow-runs lookup. Do not infer CI status for main from PR CI.
- PR #167: open, Draft, not merged. Head `381afa025a403a81f32eed4bfa2c44ce01a95540`; recorded base SHA `13e56f9c8d2db891dde76effc832173321f9033d`.
- PR #168: open, Draft, not merged; stacked on PR #167. Head `eb014870ef8d207e0a1e6f5986a9e83defc9b16b`; base branch `e8-180-signed-owner-commit-boundary`, base SHA `381afa025a403a81f32eed4bfa2c44ce01a95540`.
- PR #159: open, non-Draft, not merged. Head `ac827b33ca617f315de268b38618f53f47ab6a6a`; recorded base SHA `a8e5c44c94bcb288635a0c361ebe89fbdbd4875b`.

Links:
- Main: https://github.com/Autopoiesis-Intelligence/Gnosis-Core
- PR #167: https://github.com/Autopoiesis-Intelligence/Gnosis-Core/pull/167
- PR #168: https://github.com/Autopoiesis-Intelligence/Gnosis-Core/pull/168
- PR #159: https://github.com/Autopoiesis-Intelligence/Gnosis-Core/pull/159

## 2. Exact CI evidence

For PR #168 head `eb014870ef8d207e0a1e6f5986a9e83defc9b16b`:
- CI run #3616, run ID `38248625783`: Python 3.11 passed (992 tests); Python 3.12 passed (992 tests).
- Import Graph run #1868: success.
- CodeQL run #2497: success.
- Dependency Review run #1038 / ID `38248625769`: failure. The PR description reports a known Dependency Graph/configuration issue; that failure alone does not prove a vulnerable dependency.
- Earlier intermediate commit `4b926cbe...` had malformed literal escaped newlines in a test; corrected by `eb014870...`. Do not treat the intermediate failure as current-head CI evidence.
- These results are for PR #168's exact head and do not establish that current main is green, nor prove production runtime integration.

For PR #159:
- CI run #3537 / ID `38054572940` used merge commit `02f90444e67d6580fb6c9ff9dbb85a5f1d373085`, combining PR head `ac827b33...` and old base `a8e5c44...`.
- Python 3.11: 1057 passed, 33 failed, 2 errors; job failed.
- Python 3.12 was cancelled by matrix fail-fast; no complete result for that job.
- This is old merge-commit evidence, not direct CI on current main or a fresh merge base.

For main HEAD `00648d141...`: workflow lookup returned no associated runs. Current-main CI is therefore UNKNOWN from this check.

## 3. Reconciliation findings

1. The chat's prior label “SEQ 265” was not located as a canonical repository sequence marker. Treat it as a conversational label, not authoritative project state.
2. Main has advanced beyond the base recorded by PR #167. A GitHub compare between `381afa025a...` and current main `00648d141...` reports diverged history. Do not assume a simple fast-forward or merge-safe relationship; inspect graph/diff and refresh the PR bases deliberately.
3. PR #168 is stacked on #167. Do not merge #167 alone as though it completes production integration: its own scope explicitly says the production gate did not yet invoke the verifier and did not atomically consume nonce.
4. PR #168 describes signed authorization verification and atomic nonce consumption in the SQLite commit transaction, with focused integration tests. This is meaningful implementation evidence, but its production trust dependencies are caller-injected; a protected application/composition root provisioning these dependencies has not been identified in this repository.
5. `AuthorizationValidity.validity_evidence_digest` independent provenance remains unresolved. The expected digest must not be derived from the request or from the record being checked.
6. The product boundary ADR and context-recovery MVP are present in PR #168, not on current main at the paths referenced in the PR description. Their presence in a PR is not equivalent to acceptance/merge.
7. PR #159 is the context-continuity implementation track; it remains open and has failing old merge-commit CI. Its metadata-only external references are not authority and do not imply reference resolution or target-content attachment.

## 4. Accepted and unaccepted state

- Signed authorization primitive: IMPLEMENTED; focused tests exist.
- PR #168 commit-path integration and nonce rollback/replay tests: IMPLEMENTED; exact-head CI passed on both Python versions.
- PR #168 production trust composition: NOT PROVEN / UNRESOLVED.
- Independent validity-evidence provenance: UNRESOLVED.
- PR #168 end-to-end production execution acceptance: BLOCKED.
- Context recovery MVP: first slice implemented in PR #168; full product acceptance not established.
- PR #159 context recovery branch: open; old merge CI failed; current-base status UNKNOWN.
- Current main CI: UNKNOWN from the lookup performed for this checkpoint.
- No production-ready claim is justified by these facts.

## 5. Next sequence — reconciliation first, no speculative code

Do these in order:

1. Refresh current main HEAD and PR metadata at execution time.
2. Compare current main, PR #167, and PR #168 by merge base, changed files, commits, and CI on the exact relevant SHAs. Explicitly determine the safe stack/base update plan; do not merge the stack in the wrong order.
3. Inspect the current Dependency Review failure details and distinguish repository configuration failure from a real dependency finding.
4. Identify the actual deployable application/composition root, if any, that owns issuer-key lifecycle/status, trusted scope/policy, trusted time, and independent validity-evidence source. Repository absence is not proof that no external application exists.
5. If no concrete application boundary exists, keep production composition BLOCKED and write the minimal contract/acceptance tests before implementing a provider. Do not invent trust roots or weaken fail-closed behavior.
6. For PR #159, compare the 33 failures with current main before attributing regressions to the branch; rerun on a fresh merge base after the comparison.
7. Record resulting SHA, exact CI run URL, runtime evidence, persistence evidence, and what remains unproven. Do not assign a new canonical SEQ number unless the repository's sequence mechanism defines it.

## 6. Non-negotiable evidence protocol

DESIGN → IMPLEMENTED → REACHABLE → RUNTIME → PERSISTED → AUDITED → CI_PROVEN.

Selection is not verification; authorization binding is not authority provenance; persistence is not execution proof; structural replay is not event authenticity; synthetic PASS is not runtime evidence; green CI is not production acceptance.

A chat transfer is a recovery aid, not proof. If this document conflicts with live repository refs, source, CI, or runtime evidence, reconcile it and update the checkpoint.


## 7. Follow-up investigation — 2026-10-12 (after initial checkpoint)

### Dependency Review failure: exact cause now verified

Fetched job log for workflow run ID `38248625769`, job ID `114808802326`. The action exits with:
`Dependency review is not supported on this repository. Please ensure that Dependency graph is enabled`.

Therefore this run does **not** report a high-severity dependency finding. It is a repository capability/configuration failure: GitHub's Dependency Graph is disabled or unavailable. The workflow file `.github/workflows/dependency-review.yml` uses `actions/dependency-review-action@v5` with `fail-on-severity: high`. Keep the security gate; the proper next action is to enable Dependency Graph in repository Settings → Security (if authorized/available), then rerun. Do not silently disable the check or lower its severity.

### Current main source: authorization boundary still not integrated

Fetched current-main files at observed HEAD `00648d14106de03e194c58d90790d2fe202670a4`:
- `gnosis/reflection/execution_adapter.py` calls `require_trusted_execution(request, conn=conn, actor=actor)` without a production trust context.
- `gnosis/reflection/trusted_execution_gate.py` obtains `expected_policy_version` and `expected_evidence_digest` from the same `AuthorizationValidity` object it validates. This is not an independent trust source.
- `gnosis/reflection/owner_authorization.py` is absent on current main (GitHub contents API returned NOT_FOUND).
- `gnosis/context/cli.py` on main is the old compact JSON emitter without the opt-in source-document flag from PR #168.
This independently confirms the E8.180/E8.181 work is not integrated into current main.

### Branch relationship is explicitly diverged

GitHub compare endpoint:
- `main` vs `e8-180-signed-owner-commit-boundary`: status `diverged`, branch is 6 commits ahead and 3 behind; merge base `838f3f2b3405fb5f43fe85f7316c68f5a53ac1e1`. Four files changed by the PR #167 head.
- `e8-181-production-trust-context` is 68 commits ahead of its PR #167 base branch ref `381afa025a403a81f32eed4bfa2c44ce01a95540`, with no behind commits relative to that base. This is a stacked branch, not a standalone change against current main.
- PR #167 remains Draft/open and is not merge-ready until base divergence is reconciled.
- PR #168 remains Draft/open and must be reviewed as a dependent stack. Do not merge it independently or assume its passing tests mean the feature is live on main.

### Governance/phase-ledger conflict

Current `docs/PHASE_LEDGER.md` says the active phase is `CONTEXT-CONTINUITY ARCHITECTURE` and explicitly forbids identity/authentication/authorization implementation, while open PRs #167/#168 implement owner authorization and execution-gate integration. This is a scope-governance conflict, not a code defect to resolve by inference. Before further auth-code changes, the project owner/authorized integration gate must explicitly reconcile the phase scope in durable project docs. Do not treat broad chat permission as silently superseding the repository's phase ledger.

### Revised next actions

1. Decide/reconcile the phase-ledger scope conflict in durable project state before more authorization implementation.
2. Refresh main and PR refs; inspect full commit/file diffs and merge bases, then plan a safe stack rebase/update. Do not force-update either branch without a verified plan.
3. Enable GitHub Dependency Graph in repository settings if permitted; rerun Dependency Review and record the exact run.
4. Only then continue the context recovery MVP within its approved scope, or formally authorize the E8.180/E8.181 authorization track.
5. Production trust composition remains BLOCKED until an actual protected composition root and independent sources are found or implemented and tested.
