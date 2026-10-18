# Gnosis-Core Execution Queue

This file is the persistent, human/agent-editable task ledger for the next Self-Learning / Self-Evolution work.
It is **not yet an executable queue**: no task may be claimed as automatically picked up until a runtime consumer is implemented and demonstrated.

## Operating rules

- Keep this file in version control. Update it through a reviewed commit/PR; never treat chat history as project state.
- Work the highest-priority unblocked task first. A task is `DONE` only when its evidence fields contain exact commit SHA, CI run(s), and runtime/persistence evidence required by its acceptance criteria.
- Allowed statuses: `READY`, `IN_PROGRESS`, `BLOCKED`, `DONE`, `REJECTED`, `SUPERSEDED`.
- `BLOCKED` must name a concrete dependency or missing authority. Do not use it as a generic parking state.
- A failing test is a defect signal, not permission to weaken the invariant. Preserve regression coverage.
- Separate isolated/sandbox evolution from production execution. Never manufacture trusted-owner authorization, trust roots, trusted time, or execution proof to make a test pass.
- No database schema, migration, runtime authority, or persistence-contract changes without the required architectural authorization. Existing application-provided DB connection remains the checkpoint storage decision.
- Keep the evidence ladder explicit: DESIGN → IMPLEMENTED → REACHABLE → RUNTIME → PERSISTED → AUDITED → CI_PROVEN.
- Reorder tasks only when new repository/runtime evidence justifies it. Record the reason in the task's notes.

## Current objective

Make the Self-Learning / Self-Evolution path execute a real, bounded learning cycle, preserve its resulting state/evidence, and make failures actionable. Then add a queue consumer only after its input contract, authority boundary, and runtime behavior can be demonstrated.

## Queue

### GNOSIS-SELF-001 — Restore canonical evolution identity parity
- **Priority:** P0
- **Status:** IN_PROGRESS
- **Objective:** Resolve the mismatch between provenance identity construction and the execution gate's canonical digest.
- **Dependencies:** Existing proposed fix in PR #249; validate against current `main`, not its historical base.
- **Acceptance criteria:**
  1. Confirm the exact current `main` SHA and compare PR #249 against it.
  2. Regression test covers empty and explicit evaluator identity fields.
  3. Exact-head CI results are collected; failures are classified rather than hidden.
  4. A real execution-path test demonstrates the canonical identity reaches the intended gate.
- **Evidence:** PR https://github.com/Autopoiesis-Intelligence/Gnosis-Core/pull/249, exact current head `63779be3d8c381039fa656134990e85ddab76003`, base/main `cf091b9f556de3f412f96dbf1a7744799b217c6e`. CI run `39092565603`, Python 3.11: **941 passed / 24 failed / 2 errors (FAIL)**; Python 3.12 was cancelled after the test job failed. Compared with prior head run `39091467887` (939 passed / 26 failed / 2 errors), two fixture failures disappeared after adding required `evidence=()`; overall suite remains red. CodeQL run `39092565599` passed; Import Graph run `39092565602` passed; Dependency Review run `39092565591` failed because Dependency Graph is disabled. The canonical identity tests and fixture correction are narrow evidence only, not full execution-path or end-to-end evolution proof. Follow-up commit `63779be3d8c381039fa656134990e85ddab76003` adds the complete `EvidenceProvenance` mapping (including `parent_state_id`, status fields, content/binding identity and `evolution_identity`) to the persisted-chain test fixture; exact-head CI run `39092847814` completed FAIL on Python 3.11; Python 3.12 was cancelled after test failure. The job log endpoint currently returns `BlobNotFound`, so the exact post-fix test count and whether the `parent_state_id` error disappeared are NOT VERIFIED. Diagnostic run `39092845560` failed on Python 3.11 with 493 passed / 7 failed; Python 3.12 cancelled.
- **Notes:** Keep IN_PROGRESS. The exact canonical-identity test passes, but production execution tests still fail elsewhere, including a trusted validity requirement and tamper-policy test.

### GNOSIS-SELF-002 — Reproduce and classify the current Self-Evolution failure set
- **Priority:** P0
- **Status:** IN_PROGRESS
- **Objective:** Run the current test/CI suite at an exact SHA and map each failure to a production path, stale test/API contract, or environment/fixture issue.
- **Dependencies:** GNOSIS-SELF-001 current-head reconciliation can run in parallel with failure classification, but do not merge unverified changes.
- **Acceptance criteria:**
  1. Record exact SHA, workflow/run IDs, Python versions, pass/fail/error counts.
  2. Group failures by root cause and identify the smallest reproducible test for each group.
  3. Keep security, persistence, recovery, and replay failures visible; do not relax assertions merely to obtain green CI.
  4. Publish a prioritized fix list in this file.
- **Evidence:** PR #249 exact head `63779be3d8c381039fa656134990e85ddab76003`, base/main `cf091b9f556de3f412f96dbf1a7744799b217c6e`. CI run `39092565603`, Python 3.11: **941 passed / 24 failed / 2 errors (FAIL)**; Python 3.12 cancelled after the test job failed. Previous head run `39091467887`: **939 passed / 26 failed / 2 errors (FAIL)**. The two `EvolutionEvidence` missing-argument failures disappeared after the test-only fixture correction (`evidence=()`); no production code/invariant changed. Self-Diagnostic run `39092563013`, Python 3.11: **493 passed / 7 failed**; Python 3.12 cancelled. CodeQL `39092565599` and Import Graph `39092565602` passed; Dependency Review `39092565591` failed due to disabled repository Dependency Graph. PR #251 exact head `7341b010ed163e9295249599baff76174817e032`, CI run `39092347457`, Python 3.12: **932 passed / 32 failed / 2 errors (FAIL)**; Python 3.11 failed/cancelled after test failure. Diagnostic run `39092341957` failed: Python 3.11 **494 passed / 6 failed**; Python 3.12 cancelled. Target test `test_execution_adapter_fails_closed_without_owner_authorization` passes on PR #251 and failed on earlier base diagnostic run `39080280460` at SHA `1c1b5bd0deb887a3a55b3fae3eb0f408b52349f5` with `AttributeError: 'object' object has no attribute 'execute'`. This is a narrow, reproducible improvement; the full suite remains red. Dependency Review run `39092347430` explicitly reports that it is unsupported while repository Dependency Graph is disabled (configuration issue, not a test failure). Import Graph and Contract Database passed on PR #251; CodeQL was still in progress at last check.
- **Failure clusters observed:** (1) canonical provenance/authorization binding and tamper rejection; (2) endogenous candidate-to-proposal binding and evolution-memory contract mismatch; (3) persistence/recovery/replay and audit-key collisions; (4) stale or mismatched APIs in reflection/recovery tests; (5) real-commit failure-injection errors. Keep these separate and identify the owning implementation/test contract before edits.
- **Next action:** Do not edit the gate until the independent trust-input contract is authorized; hard-coded or self-derived expected digests are rejected approaches. Continue with a separate narrow persistence fix only after inspecting the exact verifier/writer contract for `parent_state_id`. Keep PR #249/#250/#251 open and unmerged while test CI is red.

### GNOSIS-SELF-003 — Demonstrate a bounded end-to-end learning cycle in an isolated runtime
- **Priority:** P0
- **Status:** IN_PROGRESS
- **Objective:** Make one reproducible Self-Learning / Self-Evolution cycle actually run through candidate → test → select → evolve → verify, using only an explicitly isolated test/sandbox authority boundary where production authorization is unavailable.
- **Dependencies:** GNOSIS-SELF-001; relevant root causes from GNOSIS-SELF-002.
- **Acceptance criteria:**
  1. A documented command starts the cycle from a clean, reproducible state.
  2. The run records the input state, candidate, test outcome, selection rationale, resulting state, and provenance.
  3. A no-op candidate cannot be counted as evolution.
  4. The test distinguishes successful sandbox execution from production-authorized execution.
  5. A second run can inspect/reconstruct the persisted result; evidence is not inferred from an in-memory object alone.
- **Evidence:** PR #249 current head `63779be3d8c381039fa656134990e85ddab76003` contains canonical identity parity, immutable `Mapping` acceptance for proposal binding, durable-memory `state_id` projection, and a test-fixture correction. Exact-head CI run `39092933211` on `63779be3d8c381039fa656134990e85ddab76003`: Python 3.11 **941 passed / 24 failed / 2 errors**, Python 3.12 cancelled. The `parent_state_id` failure disappeared from the current failure summary after the test-only mapping correction, but the end-to-end cycle remains unproven. Job log `117573310959` from run `39092933211` gives exact remaining E9 failures: (a) `test_two_evolution_cycles_preserve_memory_causality_across_restart` and `test_e9_restart_reflection_consumes_persisted_endogenous_memory` fail because they omit required `proposal_report_id`; (b) `test_endogenous_provenance_persists_and_replays_after_restart` and `test_e9_second_cycle_completes_persistent_transaction_and_memory` fail in production `gnosis/evolution/replay.py:63` because `replay_complete()` accesses `execution.execution_id`, absent from `SandboxExecution`; the same function then accesses additional absent fields `evaluation_status`, `shadow_status`, `invariant_status`, `governance_decision`. `SandboxExecution` in `gnosis/evolution/sandbox.py` currently contains only candidate/state digests, operations, status, evidence digest, and observations. This is not just a test fixture issue: replay's runtime contract is inconsistent with the actual sandbox object. Fix requires a deliberate, narrow contract decision: either pass independently bound execution/status fields into replay, or make the sandbox result carry the necessary fields from a trusted construction path; do not infer authority/status from observations or fabricate IDs. Proposal provenance scope and other persistence/recovery failures remain, so no bounded end-to-end cycle is proven. PR #251 separately contains a fail-closed preflight guard; its exact-head CI run `39092347457` remains red (932 passed / 32 failed / 2 errors on Python 3.12), while the targeted missing-owner-authorization regression passes. Neither branch has been merged.
- **Next action:** Keep the production trusted-gate change blocked until an independent policy/evidence source is authorized. Separately review PR #251's preflight guard as a narrow fail-closed improvement. Then isolate one persistence defect (first `parent_state_id` chain verification) with a focused test; do not combine unrelated changes or claim end-to-end runtime.
- **Notes:** Do not bypass the trusted-owner gate or claim production commit authority. If the current code cannot run the cycle, fix the narrowest real blocker and retain a regression test.

### GNOSIS-SELF-004 — Repair durable state, provenance, recovery, and replay defects
- **Priority:** P1
- **Status:** READY
- **Objective:** Fix persistence/recovery/replay defects found by GNOSIS-SELF-002 without confusing stored records with ingestion, execution, or event authenticity.
- **Dependencies:** GNOSIS-SELF-002 root-cause list; architectural approval before any schema/migration or persistence-contract changes.
- **Acceptance criteria:**
  1. Each fix has a focused regression test.
  2. Repeated recovery requests for different subjects do not collide on a global audit key.
  3. Recovery/replay checks verify subject binding and provenance, not just structural shape.
  4. A fresh process can read persisted state and verify the expected linkage.
  5. Runtime evidence and CI evidence are recorded separately.
- **Evidence:** Previous exact-head CI run `39092847814` logged `malformed persisted chain: 'parent_state_id'` from an incomplete test mapping. Follow-up test-only commit `63779be3d8c381039fa656134990e85ddab76003` adds required fields to both persisted-chain verifier calls; latest CI run `39092933211` no longer lists that KeyError, though the suite remains red (941 passed / 24 failed / 2 errors). Current endogenous-memory failures are contract-level: `append_evolution_memory` requires `proposal_report_id` and validates that the persisted report actually contains `proposal_id`. Further source review shows the test fixtures also pass `tx.audit_record.record_digest` as `transition_id`, but `append_evolution_memory` resolves that ID through the canonical `transitions` table and validates the linked candidate/state. Merely adding `proposal_report_id` is therefore insufficient: the fixture must create a real canonical transition and persist a real ReflectionReport containing the proposal, then pass both actual IDs. The tests also call memory with `state_id=candidate.parent_state_id`, which must be checked against the canonical transition's `to_state_id`. Separately, two replay tests expect `SandboxExecution.execution_id`, but the actual dataclass has no such field; classify whether the test should use a canonical execution identity from provenance or whether a contract change is needed. No schema or migration change authorized. Other observed clusters include `proposal provenance scope is required`, `recover_instance()` missing required `authorization`, `conflicting audit replay`, and rejected/no-op transition count mismatches. No schema or migration changes authorized.

### GNOSIS-SELF-005 — Resolve production execution-authority provenance gap
- **Priority:** P1
- **Status:** BLOCKED
- **Objective:** Establish a real, independently trusted authorization source for production execution rather than deriving expected trust values from the same object being validated.
- **Dependencies:** Requires an explicit trusted-owner / trust-bundle contract and legitimate provisioned authority material. No credentials or authority material may be invented.
- **Acceptance criteria:**
  1. The expected policy/evidence digest comes from an independent trusted source.
  2. Issuer identity, key version, scope, policy version, evolution identity, parent-state digest, request provenance, validity window, nonce, and signature are bound and verified.
  3. The production composition root supplies the trust source; a disconnected verifier is not enough.
  4. Tampered policy, stale parent state, replayed nonce, expiry, and wrong scope are rejected in regression and integration tests.
- **Evidence (source audit 2026-10-18):** `main` SHA `cf091b9f556de3f412f96dbf1a7744799b217c6e` and PR #249 head `63779be3d8c381039fa656134990e85ddab76003` both contain the same `gnosis/reflection/trusted_execution_gate.py` logic: `require_valid(expected_policy_version=validity.policy_version, expected_evidence_digest=validity.validity_evidence_digest)`. Both expected values are read from the submitted `AuthorizationValidity`, so the check cannot independently detect a forged policy/evidence value. Regression `tests/test_trusted_execution_gate_tamper.py::test_tampered_policy_is_rejected_before_consumption` constructs `AuthorizationValidity("auth-t", "policy-forged", "ev-1")` and expects rejection, but exact-head CI run `39092565603` reports `DID NOT RAISE PermissionError`. `gnosis/reflection/authority.py::issue_execution_authorization` still raises `NotImplementedError("trusted owner-authority issuer is not implemented")`; the gate receives no independent expected policy/evidence source. Source defect + failing CI are confirmed; no runtime exploit test was performed.
- **Blocker:** Independent trust source and owner-authority contract/provisioned material are not established. Do not patch by hard-coding expected digests or by treating fields on the submitted object as independent authority. Resolve the authorized contract first, then pass independently sourced expected policy/evidence into validation and retain tamper/replay/expiry tests.

### GNOSIS-SELF-006 — Add a runtime consumer for this queue
- **Priority:** P2
- **Status:** BLOCKED
- **Objective:** Let the project discover and process eligible tasks from this ledger, while preserving governance, evidence, and safe stopping behavior.
- **Dependencies:** Demonstrated bounded cycle (GNOSIS-SELF-003), approved task schema/contract, and explicit authorization for any runtime/persistence changes.
- **Acceptance criteria:**
  1. Consumer parses and validates task IDs, statuses, dependencies, and acceptance criteria.
  2. Only eligible tasks are selected; selection is not execution or proof of progress.
  3. Every attempt emits durable start/result/failure evidence with correlation IDs.
  4. Failed or ambiguous tasks stop safely and remain inspectable; no silent no-op.
  5. A restart can recover queue state using the existing application-provided DB connection, without unapproved schema/migration changes.
  6. Integration test proves a task is actually consumed, executed, and reconciled with the ledger.
- **Evidence:** No confirmed runtime consumer yet.
- **Blocker:** Runtime consumer and its authorized persistence contract are not established.

## Result update template

For each task update, record:

- **Last checked:** 2026-10-18
- **Commit SHA:** exact full SHA
- **CI:** workflow name + run ID + conclusion + test counts
- **Runtime:** command/environment + observed outcome
- **Persistence:** what was read back after restart, if applicable
- **Audit:** invariant and provenance checks performed
- **Proven:** exact claims supported by evidence
- **Not proven:** remaining gaps
- **Next action:** one concrete action


### SEQ 145 — Replay/Sandbox contract correction (CI pending)
- On PR #249 branch `work/self-evolution-unblock-identity`, commit `dcd6f23d87aa7e8e0fe9bed7d1b484e1aeeaa22e` updates `gnosis/evolution/replay.py` to compute the deterministic execution identity from the sandbox's actual candidate/state/evidence fields, compare it to provenance, and use provenance's own evaluation/shadow/invariant/governance metadata only as provenance-owned fields. The audit execution identity is checked against the provenance identity (or the deterministic fallback if provenance is absent).
- CI triggered for this exact commit: run `39093201261` (CI), `39093201257` (CodeQL), `39093201264` (Import Graph), `39093201258` (Dependency Review). At last check CI job `117574109424` (Python 3.11) was in progress and `117574109593` (Python 3.12) queued; no PASS/FAIL conclusion yet.
- Scope: no schema/migration or authorization changes. This corrects interface consistency but does not prove independent authenticity of evaluation/governance statuses because SandboxExecution does not carry them; they remain provenance-owned and the replay result is consistency evidence, not authority/execution proof.
- Still outstanding: required `proposal_report_id` and canonical transition/state IDs in memory tests; broader CI failures and trusted authority boundary remain unresolved. Do not merge while CI is red or pending.
- Follow-up CI evidence for `dcd6f23d87aa7e8e0fe9bed7d1b484e1aeeaa22e`: run `39093201261`, Python 3.11 failed. The `SandboxExecution.execution_id` AttributeError is no longer listed; the replay tests now fail at stale test assertions using `ReplayResult.valid`, while the result type exposes `reproducible`. Test-only correction committed to PR #249 as `e6f683b701a592404e37021176c22366f0a9b752` (`assert replay.reproducible` / `assert rr.reproducible`). Latest exact-head workflow run for `e6f683b...` was not yet visible at time of check, so the correction is unverified. Memory provenance-scope failures remain, as do broader authority-boundary/federation/persistence failures.

### SEQ 146 — Reflection report scope fixture correction
- Exact CI run `39093236155` for prior head `e6f683b701a592404e37021176c22366f0a9b752`: Python 3.11 failed, Python 3.12 cancelled. `Import Graph` passed; `Dependency Review` failed; CodeQL was still running at last check.
- CI showed `ReplayResult.valid` test-API mismatch was addressed by test-only commit `e6f683b701a592404e37021176c22366f0a9b752` (`ReplayResult.reproducible`), but the memory-cycle test still failed because `proposal_report_id` was omitted.
- Follow-up test-only commit `e90d2bb6970a693ae9bfc1a00144b0b2d1d84ad1` now persists actual `ReflectionReport` objects through `save_reflection_report` and passes each returned report ID into the two-cycle memory test. Exact-head workflow runs were not yet visible at last check; this is not CI-proven.
- Remaining E9 tests still construct memory using `tx.audit_record.record_digest` as `transition_id` and `candidate.parent_state_id` as `state_id`. This does not satisfy the canonical `transitions` table contract. Do not fabricate transition IDs or treat audit digests as transition IDs. Next inspect whether those tests can be rebuilt around the real Instance/_persist_transition pathway without weakening provenance/authority boundaries.
- PR #249 remains open/unmerged; base SHA reported by PR tool is `cf091b9f556de3f412f96dbf1a7744799b217c6e`. Full self-evolution remains unproven.

### SEQ 147 — Persisted reflection test fixtures
- Exact-head CI run `39093303865` for `e90d2bb6970a693ae9bfc1a00144b0b2d1d84ad1`: Python 3.11 failed, Python 3.12 cancelled; `Import Graph` passed, `Dependency Review` failed, CodeQL was in progress at the prior check. Coverage report showed 5,791 statements / 609 missed / 89%.
- Failures confirmed: the two-cycle test used dynamically-created proposal objects that cannot be JSON-serialized by persisted reflection storage; E9 restart and second-cycle tests omitted `proposal_report_id`. The test now uses `RuleProposal` in the persisted two-cycle scenario and persists actual reflection reports in all three affected scenarios.
- Test-only commits on PR #249 branch: `ce8bb959e8274be4c5b5a9e5b40c418cbc2b55e4` (serializable `RuleProposal`) and `63c6153a01892967b7b3a298047c655925205d98` (E9 report IDs). Exact-head workflow runs were not visible immediately after the last commit; these changes are not CI-proven.
- E9 memory calls still use `tx.audit_record.record_digest` as `transition_id` and `candidate.parent_state_id` as `state_id`; these remain inconsistent with the canonical transition/state contract. Next repair requires constructing real canonical transitions and binding memory to `transition.to_state_id`, not weakening storage validation.
- PR #249 remains open/unmerged. Do not claim autonomous evolution runtime is operational.

### SEQ 148 — E9 typed proposal fixtures
- Exact-head CI run `39093395114` for `63c6153a01892967b7b3a298047c655925205d98`: Python 3.11 failed, Python 3.12 cancelled; coverage 5,791 statements / 593 missed / 90%. Three endogenous-runtime failures remained: one proposal-binding mismatch and two `TypeError: Object of type P is not JSON serializable` errors.
- Follow-up commit `f216913742d98ba2accc0ef21b47d22c75b5edd8` replaces dynamically-created proposal objects in both E9 persisted scenarios with typed `RuleProposal` values. This addresses JSON serialization shape, but has not yet been verified by CI.
- E9 canonical transition/state mismatch remains. Next check CI for exact HEAD `f216913742d98ba2accc0ef21b47d22c75b5edd8`, then diagnose proposal-binding mismatch in the two-cycle scenario. Do not relax `candidate_binds_proposal`, storage validation, or authority boundaries to force tests green.
- PR #249 remains open and unmerged; autonomous self-evolution runtime is not proven.

### SEQ 149 — CI after typed E9 proposals
- Exact-head CI run `39093477463` for `f216913742d98ba2accc0ef21b47d22c75b5edd8`: Python 3.11 failed; Python 3.12 cancelled. Coverage 5,791 statements / 592 missed / 90%.
- The dynamic-object serialization errors no longer appear in the reported failure summary. The three targeted scenarios still fail: two E9 tests use `tx.audit_record.record_digest` where storage requires a real row in `transitions` scoped to an instance, and the two-cycle test fails `candidate_binds_proposal` after memory history is loaded. These are distinct contract failures, not grounds to weaken validation.
- The E9 tests currently persist provenance/audit transactions but never persist the candidate's canonical transition; `persist_evolution_transaction` is not a substitute for `_persist_transition`. Next inspect/rebuild these fixtures around `Instance`, `save_instance`, `commit_endogenous_candidates`, and `_persist_transition`, then use the returned canonical `TransitionRecord.transition_id` and `to_state_id`. For the candidate binding failure, inspect how the existing state relation set changes during generation; keep the exact proposal-binding gate intact.
- PR #249 remains open/unmerged. Current checked head `f216913742d98ba2accc0ef21b47d22c75b5edd8`; self-evolution remains unproven.

### SEQ 150 — Candidate binding investigation
- Exact CI log for `39093477463` confirms the two-cycle failure occurs at `commit_endogenous_candidates(...)` in cycle 2, after the memory-evidence assertion succeeds.
- `State.with_relations()` in `gnosis/core/types.py` appends relations rather than replacing them. This explains why a later candidate state retains earlier reflection relations, but does not by itself prove the p2 mismatch: `candidate_binds_proposal()` filters by the exact proposal target. Do not change relation semantics or weaken the guard without a reproducer identifying the mismatched field.
- E9 fixture root cause is confirmed from test source: both tests pass `tx.audit_record.record_digest` as `transition_id` while no canonical `Instance`/`transitions` row is created. `persist_evolution_transaction()` only writes provenance/audit, not the canonical state transition. Correct fixture must create and persist a real transition; changing storage validation is rejected.
- Next: add a narrow diagnostic assertion for the candidate/proposal binding fields before the cycle-2 commit, and redesign E9 fixtures to create a canonical instance/transition chain rather than relabel audit records. No production guard changes authorized by this evidence.

### SEQ 151 — Fixed current-report proposal selection
- Root cause of the two-cycle binding failure is now identified: `State.with_relations()` retains earlier relations, while `commit_endogenous_candidates()` selected the *first* `proposed_rule` relation without checking whether its target belonged to the current report. On cycle 2, the retained `p1` relation could be selected before current `p2`, so the current report could not resolve it.
- Production fix committed to PR #249: `9205eda6231e89cfd6938cc90a4c647d18db3c58`. The selector now only considers proposal relations whose target exists in the supplied report; `candidate_binds_proposal()` still performs the full exact binding check. This is a targeted selection correction, not a relaxed validation.
- Awaiting CI evidence for this commit. The two E9 tests still need canonical transition rows; their audit digests remain invalid transition IDs.

### SEQ 152 — CI result and canonical E9 fixture correction
- CI run `39093670799` for proposal-selection fix `9205eda6231e89cfd6938cc90a4c647d18db3c58`: Python 3.11 failed, Python 3.12 cancelled. The two-cycle proposal-binding failure is absent from the failure summary; remaining targeted failures are the two E9 memory tests referencing a nonexistent canonical transition.
- Test-only changes committed on PR #249: `d17b9825a0748e5507f6409a65ef09152599c3de` creates a real `Instance`, persists it, commits each endogenous candidate through the existing engine selector, persists its canonical transition with `_persist_transition`, and uses the returned `transition_id` / `to_state_id` for evolution memory. Follow-up `e5b0336297c38b281dc064bc7c781216e45b163c` scopes memory reads to the actual generated instance ID.
- These changes are not yet CI-proven. Next inspect the new run and fix only concrete failures. No authority-boundary changes; no merge.

### SEQ 153 — E9 fixture follow-up
- Latest test-only commits on PR #249: `d17b9825a0748e5507f6409a65ef09152599c3de` (create/persist real canonical transitions for E9 memory) and `e5b0336297c38b281dc064bc7c781216e45b163c` (use generated canonical instance ID), followed by `9527b0307776b3fdcd671dd0130b31d689aaad07` (same canonical instance ID when reloading the two-cycle E9 memory).
- The previous exact CI run `39093670799` no longer showed the two-cycle proposal-binding failure; it still failed on the two invalid E9 transition references. New CI runs for the latest fixture commits have not yet appeared in the commit-run lookup at this check, so these edits are not CI-proven.
- Next verify CI for `9527b0307776b3fdcd671dd0130b31d689aaad07`; inspect exact failing test logs and correct any canonical-head/instance-ID issues. Keep PR draft and unmerged.

### SEQ 154 — Exact-head CI reconciliation
- CI run `39093787178` for PR #249 HEAD `9527b0307776b3fdcd671dd0130b31d689aaad07`: Python 3.11 FAIL; Python 3.12 cancelled. Coverage: 5,791 statements, 593 missed, 90%. Import Graph `39093787166` PASS; CodeQL `39093787172` still in progress at inspection; Dependency Review `39093787183` FAIL (repository Dependency Graph configuration).
- Both targeted E9 tests now PASS in that CI: `test_e9_restart_reflection_consumes_persisted_endogenous_memory` and `test_e9_second_cycle_completes_persistent_transaction_and_memory`. The earlier two-cycle causality test also PASSes. This proves those test scenarios only, not autonomous production self-evolution.
- Remaining CI failures are cross-cutting and not safe to patch blindly: authority-boundary failures involving missing/invalid authorization; federation trusted-gate test; memory test calling nonexistent `Engine.generate_candidates`; persistence/recovery contract mismatches (`recover_instance` now requires authorization, stale-head replay, transition counts, audit replay); reflection-gate calls missing required authorization/now; policy-tamper rejection; and two real-commit failure-injection tests cannot run because `real_commit_fixture` is not defined in `tests/conftest.py`.
- Do not change fail-closed authority behavior or relax required authorization merely to satisfy old tests. Next task: reconcile test expectations against current API contracts and build the missing real-commit fixture only from an existing valid authorized-commit setup; first inspect the current authority adapter tests and exact fixture requirements. Keep PR #249 draft/unmerged.

### SEQ 155 — Real-commit rollback fixture added; CI pending
- Commit on PR #249 branch: `b4a1bbc6d12197748ca9906ad1e76a8983e2dcf7`; changed only `tests/conftest.py`.
- Added the missing `real_commit_fixture` using the existing adapter's real SQLite commit path, canonical candidate/provenance binding, and an explicit `AuthorizationValidity` record. Failure injection is passed through a mutable test wrapper because `ExecutionCommitRequest` is frozen.
- The fixture docstring explicitly states this is a test-only directly constructed authorization; it does NOT prove or implement the missing production trusted-owner issuer.
- Not yet proven: rollback assertions, fixture compatibility with `record.transition_id`, and overall CI. Wait for Actions on the new exact HEAD before further changes.
- Next SEQ 156: inspect CI for commit `b4a1bbc6d12197748ca9906ad1e76a8983e2dcf7`; if rollback tests run, use their exact failures to decide whether the fixture or production transaction path is defective. Keep PR #249 draft/unmerged.
