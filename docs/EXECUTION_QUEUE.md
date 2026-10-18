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
- **Evidence:** PR https://github.com/Autopoiesis-Intelligence/Gnosis-Core/pull/249, head `f398c0df464692c5dcd78b2e7b1d28b9cdc3d70e`, base `cf091b9f556de3f412f96dbf1a7744799b217c6e`; compare confirms the head is 5 commits ahead and 0 behind current `main`. CI run `39091467887`, Python 3.12: **939 passed / 26 failed / 2 errors (FAIL)**; Python 3.11 cancelled. The new canonical identity parity test and evaluator-identity persistence/recovery tests passed. Import Graph and CodeQL passed; Dependency Review failed because Dependency Graph is disabled. This verifies the narrow identity regression tests, not the full execution path or end-to-end evolution.
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
- **Evidence:** PR #249 previous head `f398c0df464692c5dcd78b2e7b1d28b9cdc3d70e`, CI run `39091467887`, Python 3.12: **939 passed / 26 failed / 2 errors (FAIL)**; Python 3.11 cancelled. New head `7055712b6736ca81721302da699000dde4dda8a6` adds explicit `evidence=()` to two `EvolutionEvidence` test fixtures that were incompatible with the required constructor; no production code or invariant was changed. Exact-head CI runs `39092565603` (CI) and `39092563013` (Self-Diagnostic) are queued/in progress; outcome pending. PR #251 exact head `7341b010ed163e9295249599baff76174817e032`, CI run `39092347457`, Python 3.12: **932 passed / 32 failed / 2 errors (FAIL)**; Python 3.11 failed/cancelled after test failure. Diagnostic run `39092341957` failed: Python 3.11 **494 passed / 6 failed**; Python 3.12 cancelled. Target test `test_execution_adapter_fails_closed_without_owner_authorization` passes on PR #251 and failed on earlier base diagnostic run `39080280460` at SHA `1c1b5bd0deb887a3a55b3fae3eb0f408b52349f5` with `AttributeError: 'object' object has no attribute 'execute'`. This is a narrow, reproducible improvement; the full suite remains red. Dependency Review run `39092347430` explicitly reports that it is unsupported while repository Dependency Graph is disabled (configuration issue, not a test failure). Import Graph and Contract Database passed on PR #251; CodeQL was still in progress at last check.
- **Failure clusters observed:** (1) canonical provenance/authorization binding and tamper rejection; (2) endogenous candidate-to-proposal binding and evolution-memory contract mismatch; (3) persistence/recovery/replay and audit-key collisions; (4) stale or mismatched APIs in reflection/recovery tests; (5) real-commit failure-injection errors. Keep these separate and identify the owning implementation/test contract before edits.
- **Next action:** Inspect exact-head CI for `7055712b6736ca81721302da699000dde4dda8a6`; verify whether the two fixture failures disappear. Then take the next highest-impact failure cluster from current tracebacks. Do not merge either PR while full CI and trusted-execution checks remain red.

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
- **Evidence:** PR #249 now contains focused fixes on branch head `f398c0df464692c5dcd78b2e7b1d28b9cdc3d70e`: canonical evolution identity parity, immutable `Mapping` acceptance for proposal binding, and preservation of `state_id` in durable-memory projection. Regression coverage added for identity parity and projected state identity. These are implementation changes, not end-to-end runtime proof. Previous CI run `39091313289` on earlier head `ad30ce086bf5bdc008130ec34f74e31f9c1ec29b` failed on both Python versions; exact-head CI for `f398c0d` pending.
- **Next action:** Review exact-head CI, then fix the smallest remaining memory/replay defect and execute the bounded cycle through persistence/restart.
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
- **Evidence:** CI run `39091313289` (previous PR head) reproduced chain-verifier failure `malformed persisted chain: 'parent_state_id'`, missing proposal provenance scope in memory writes, and recovery/audit replay failures. Exact-head rerun pending. No schema or migration changes authorized.

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
- **Evidence:** Historical source audit found `issue_execution_authorization()` unimplemented and self-referential trust expectations; refresh against current source.
- **Blocker:** Trust-root provisioning/owner-authority contract has not been established in current evidence.

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

- **Last checked:** YYYY-MM-DD
- **Commit SHA:** exact full SHA
- **CI:** workflow name + run ID + conclusion + test counts
- **Runtime:** command/environment + observed outcome
- **Persistence:** what was read back after restart, if applicable
- **Audit:** invariant and provenance checks performed
- **Proven:** exact claims supported by evidence
- **Not proven:** remaining gaps
- **Next action:** one concrete action
