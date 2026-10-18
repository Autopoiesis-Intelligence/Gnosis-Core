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
