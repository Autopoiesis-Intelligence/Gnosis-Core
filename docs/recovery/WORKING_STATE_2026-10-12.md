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


## 8. Context-recovery MVP contract review — 2026-10-12

Reviewed the actual PR #168 branch files `gnosis/context/snapshot.py`, `tests/test_context_snapshot.py`, `docs/product/PRODUCT_MVP_CONTEXT_RECOVERY.md`, and `docs/architecture/ADR-001-CORE-PRODUCT-BOUNDARY.md`.

### What is implemented in the inspected branch

- The snapshot is read-only at source level: it reads three documents, obtains Git metadata through subprocess calls, and does not initialize Core storage.
- It separates claims from status/source fields and returns UNKNOWN for unstructured active task, implementation, verification, acceptance, and findings.
- It detects repository-identity conflicts between the Git remote and repository labels in canonical documents rather than silently choosing one.
- Raw source documents are opt-in.
- The product MVP document defines acceptance criteria and explicitly states that product acceptance remains pending.

### Concrete test-quality gap

In `tests/test_context_snapshot.py`, `test_snapshot_is_compact_and_claims_have_source_references` uses `assert snapshot["head"] != "UNKNOWN"`. But `head` is a dictionary claim object, so this assertion passes even when its value is UNKNOWN. It should assert `snapshot["head"]["value"] != "UNKNOWN"` (and ideally validate a full SHA shape). This is a real test weakness, not proof the implementation is wrong.

### Acceptance gaps remain

- The implementation intentionally returns UNKNOWN for active task and open findings because no accepted structured source exists. Therefore the MVP does not yet deliver the full six-question handoff; it delivers repository/phase metadata and explicit unknowns.
- The branch's context recovery tests and authorization integration are bundled in PR #168. Since the current phase ledger explicitly excludes authorization implementation, future work should isolate context-recovery scope from the E8 authorization stack rather than treating the whole PR as one approved unit.
- The main-branch `AI_CONTEXT.md` contains a stale repository identifier. Given the conflict-detection rule, a real run may correctly report repository identity as CONFLICT/UNKNOWN until canonical handoff documents are corrected. This is desirable fail-safe behavior, but the conflict must be resolved in canonical documentation before claiming a clean recovery UX.
- The real-checkout test currently checks JSON schema version and HEAD shape, but does not assert repository conflict behavior, read-only Git status, or absence of database side effects on the real checkout. Fixture coverage does check status and database absence; keep the distinction clear.
- Passing CI at a historical code-test SHA cannot be attributed to later branch heads or establish acceptance of the bundled PR.

### Safe next action within the current phase

Do not merge or rebase the authorization stack yet. The smallest useful implementation task is to separate the context-recovery MVP into a branch based on current main, strengthen the false-positive HEAD assertion, and add a contract test for stale repository identity/conflict output. First verify the current main SHA and ensure the isolated patch touches only the context CLI/snapshot/tests and narrowly scoped docs. Run focused tests and CI on the exact resulting SHA; keep MVP acceptance pending until the documented acceptance criteria are satisfied.

## 9. Isolated context-recovery MVP branch — 2026-10-12

### Exact refs and scope

- Rechecked current main via GitHub commit search: 00648d14106de03e194c58d90790d2fe202670a4 remains the observed latest commit (chore: refresh current partner contract block, created 2026-10-12T07:22:03Z).
- Created branch mvp/context-recovery-isolated-2026-10-12 from that exact SHA.
- Opened Draft PR #170: https://github.com/Autopoiesis-Intelligence/Gnosis-Core/pull/170
- PR #170 base SHA: 00648d14106de03e194c58d90790d2fe202670a4.
- Current observed PR head SHA: f5b9f14065fa712d04ba3e5c9e82613d1e8a25d2.
- Compare main → PR #170 head: ahead by 4 commits, behind by 0; exactly three files changed: gnosis/context/cli.py, gnosis/context/snapshot.py, tests/test_context_snapshot.py.
- No authorization files or Core execution-gate files are changed in this isolated PR.

### Changes and verification state

- Ported the evidence-aware schema-v1 snapshot and opt-in source-document CLI from the context recovery slice, without the authorization stack.
- Added six focused tests for compact output/source references, stale repository identity conflict, missing sources, opt-in raw documents, CLI read-only/no-database side effects, and real-checkout execution.
- Corrected the HEAD assertion to validate snapshot[head][value] against a 40-character hexadecimal SHA, rather than comparing the enclosing dictionary with the string UNKNOWN.
- During authoring, a leading quote was introduced in the snapshot module docstring; it was detected by reading back the exact branch file and corrected in a follow-up commit before opening/reviewing the PR head.
- Exact-head workflow lookup for f5b9f14065fa712d04ba3e5c9e82613d1e8a25d2 returned no workflow runs; combined commit status also returned no statuses. Therefore CI is PENDING/NOT OBSERVED, not PASS. PR #170 remains Draft and unaccepted.
- No local pytest or runtime command was executed in this tool session. The tests are authored but not yet proven to pass.
- PR #170 was observed mergeable after the initial creation response; this is metadata only, not approval to merge.

### Remaining acceptance gaps

- Active task and open findings still return UNKNOWN because no accepted structured canonical source exists. This is a deliberate fail-safe, but it means the full product recovery scenario is not yet accepted.
- Main's stale repository identifier may correctly produce CONFLICT/UNKNOWN until canonical handoff docs are reconciled.
- Next action: inspect the actual CI trigger/status after GitHub Actions processes PR #170; if checks start, inspect exact-head jobs/logs, fix only evidenced failures, and record the resulting exact SHA/run. Then compare the command output to all six user questions and the full product acceptance criteria.
