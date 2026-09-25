[object Object]

## Gate 5A — Recovery Authorization Contract

### Required semantics

Recovery is a **read/reconstruction operation** only after authorization has been established; it must never silently become a mutation path.

Required authorization record:
- `authorization_id`: unique immutable identifier;
- `subject`: instance being recovered;
- `requested_by`: explicit principal;
- `authority`: governance authority/capability that permits recovery;
- `decision`: `allow` or `deny`;
- `reason`: machine-readable reason;
- `issued_at`: provenance timestamp;
- `expires_at`: optional bounded expiry;
- `evidence_digest`: digest binding authorization to the verified durable evidence set.

Required behavior:
1. no authorization → fail closed;
2. denied authorization → fail closed;
3. expired authorization → fail closed;
4. subject mismatch → fail closed;
5. evidence digest mismatch → fail closed;
6. recovery itself must not mutate Core state;
7. authorization decision and recovery outcome must be auditable.

### Non-goals

Do not use a boolean `authorized` flag, arbitrary caller string, owner identity alone, or an unbound external timestamp as the authorization mechanism.

### Implementation gate

The contract must first receive a concrete schema and deterministic validation tests. Only then should `recover_instance()` accept the authorization object. This prevents adding a superficial parameter that does not establish a real trust boundary.

Status: CONTRACT DEFINED / IMPLEMENTATION NOT STARTED.


## Gate 5A.1 — Authorization schema acceptance tests

Required deterministic cases:
- missing authorization → deny;
- decision=deny → deny;
- expired authorization → deny;
- subject mismatch → deny;
- evidence digest mismatch → deny;
- valid allow authorization → permit recovery;
- authorization fields are immutable for the verification operation;
- the authorization must bind to the exact verified evidence set;
- recovery must not change the canonical Core state.

Implementation remains blocked until these cases have a concrete machine-readable schema and executable tests.


### Gate 5A.2 — deterministic schema implemented

Implemented `gnosis/storage/authorization.py` with an immutable `RecoveryAuthorization` record, canonical digest, and fail-closed validator. Added `tests/test_recovery_authorization.py` covering valid allow, missing, denied, subject mismatch, evidence mismatch, expiry, immutability, and deterministic digest.

This is schema/validation evidence only. It does **not** yet grant recovery authority or integrate authorization into `recover_instance()`. Runtime integration remains a separate gate.


### Gate 5A.3 — runtime authorization integration

Recovery is now bound to the verified durable evidence digest. `recover_instance()` requires an immutable `RecoveryAuthorization`, validates it against the exact pre-recovery evidence digest, and records an auditable `recovery.execute` outcome using the requesting principal.

Regression coverage verifies:
- missing authorization fails closed;
- evidence mismatch fails closed without changing evidence;
- authorized recovery returns the same Core state;
- recovery execution is auditable.

The recovery audit event is an outcome record and is intentionally not part of the pre-recovery evidence digest bound by the authorization.

Status: IMPLEMENTED / CI UNVERIFIED.


## P0-R2 Acceptance Matrix — 2026-09-25

| Contract | Source evidence | Regression evidence | External CI/runtime evidence | Acceptance |
|---|---|---|---|---|
| state/relation integrity | present | present | missing | PROVISIONAL |
| audit-chain integrity | present | present | missing | PROVISIONAL |
| missing/duplicate audit evidence | present | present | missing | PROVISIONAL |
| semantic audit mismatch | present | present | missing | PROVISIONAL |
| accepted transition replay | present | present | missing | PROVISIONAL |
| rejected transition replay | present | present | missing | PROVISIONAL |
| conflicting transition replay | present | present | missing | PROVISIONAL |
| atomic rollback | present | present | missing | PROVISIONAL |
| crash/reopen recovery | present | present | missing | PROVISIONAL |
| recovery authorization | present | present | missing | PROVISIONAL |
| evidence-bound authorization | present | present | missing | PROVISIONAL |
| recovery non-mutation | present | present | missing | PROVISIONAL |
| recovery audit outcome | present | present | missing | PROVISIONAL |

### Acceptance rule

P0-R2 is **not ACCEPTED** while any mandatory row lacks current-main execution evidence. “Provisional” means source and regression evidence are present but the acceptance gate remains open.


## E7 consolidation gate — 2026-09-25

The active PR surface is now explicitly treated as a dependency chain, not a flat backlog:

1. E7.74 Proposal boundary (#72)
2. E7.75 Review (#73)
3. E7.76 Authorization (#74)
4. E7.77 Evidence reconciliation (#75)
5. E7.77 persistence/atomic recovery (#76)
6. E7.15 deterministic vertical slice (#77)
7. R3.1 autonomous-cycle evidence (#79)
8. CORE-MUTATION-BOUNDARY-01 (#80)
9. CORE-INTEGRATION-BOUNDARY-01 (#81)

Independent older E7 PRs (#39–#71) are historical evidence candidates and must not be treated as individually accepted until reconciled with the canonical current main.

Acceptance order:
- first establish P0-R2/current-main execution evidence;
- then reconcile E7.74→E7.77 as one continuous trust-boundary chain;
- then validate #77 against that chain;
- then review #79 against the mutation/integration boundaries;
- only after those gates begin new repository extraction.


## E7 live-PR reconciliation — 2026-09-25

Current GitHub PR topology was checked directly.

### Sequential chain
- #74 E7.76 — open, base `main`, head `a63870b`.
- #75 E7.77 — open, correctly based on #74 head `a63870b`.
- #76 E7.77-PERSIST — open, correctly based on #75 head `900823c`.

This is a coherent dependency chain, but none of #74–#76 has a submitted review, and they are not merged. They therefore remain unaccepted.

### Parallel branches requiring rebase/reconciliation
- #77 E7.15 is based directly on an older `main` SHA and is not based on the E7.74→E7.77 chain.
- #79 R3.1 is based on another `main` SHA and is not based on the E7 chain.
- #80 mutation boundary is based on another `main` SHA.
- #81 integration boundary is based on another `main` SHA.

The differing base SHAs mean these branches must be reconciled against the eventual canonical main after the sequential E7 chain is accepted. They must not be merged independently as if they were already cumulative.

### Review evidence
PRs #74–#81 currently report no submitted pull-request reviews through the available GitHub surface. This is an evidence gap, not a code verdict.

### CI evidence
The checked current/base commit for #81 reports zero status records. Current-main execution evidence therefore remains unavailable.

### Next acceptance order
1. Independently audit #74.
2. Audit #75 only against #74's exact head.
3. Audit #76 only against #75's exact head.
4. Reconcile/retarget #77, #79, #80, #81 after the sequential chain is accepted.
5. Obtain independent review + current-main CI evidence.
6. Only then consider repository extraction.


### E7.76 audit result — PR #74 — 2026-09-25

Source/diff audit found three acceptance-blocking trust-boundary gaps:
1. `expires_at` is stored but not checked at execution-validation time.
2. target freshness is caller-supplied rather than canonically bound to the authorization record;
3. declared `preconditions` are stored but not evaluated during execution validation.

Existing adversarial tests do not cover these cases. A GitHub PR comment was submitted documenting the findings. The PR cannot be accepted on current evidence.


### E7.76 remediation specification — 2026-09-25

The audit findings are now converted into an implementation contract for PR #74:
1. expiry must be validated against a deterministic supplied `now`; no wall-clock lookup inside the validator;
2. the authorized target revision must be an immutable field of `ExecutionAuthorization` and included in its canonical identity;
3. preconditions must be represented as machine-verifiable authorization evidence, not caller booleans;
4. validation must consume the live target revision/evidence and compare it to the authorization-bound value;
5. new adversarial tests must cover expired authorization, caller-forged target revision, unsatisfied precondition evidence, and canonical-identity tamper.

No acceptance until the amended PR passes these cases.


### E7.76 re-audit gate — result after remediation review attempt

Re-inspection of PR #74 head `a63870b` confirms the three previously reported gaps are still present:
- `expires_at` remains unenforced by `validate_execution_request()`;
- `authorized_target_revision` remains caller-supplied and is not part of `ExecutionAuthorization`;
- `preconditions` remain declarative/issuance-time booleans and are not verified as execution-time evidence.

Therefore the remediation contract is **NOT IMPLEMENTED** on the current PR head. E7.76 remains REQUEST CHANGES / NOT ACCEPTED. No downstream PR in the E7 chain may be accepted on top of this head.


### E7.76 remediation implementation — 2026-09-25

PR #74 branch `contract/e7-76-execution-authorization` now contains the first remediation implementation:
- `authorized_target_revision` is immutable and included in canonical authorization identity;
- expiry is checked against deterministic caller-supplied `now`;
- precondition evidence is represented by a canonical digest bound into authorization and checked at validation;
- new adversarial tests cover expiry, target-revision freshness, unsatisfied precondition evidence, and canonical identity tamper.

The implementation is on PR #74, not accepted into `main`. CI evidence for the new head is currently absent, so runtime acceptance remains open.


### E7.76 re-audit — remaining blocker — 2026-09-25

The remediation implementation addresses the original expiry/target/canonical-identity gaps, but a new trust-boundary gap remains:

`precondition_evidence_digest` defaults to a digest of the declared precondition strings. That is not evidence that the preconditions are actually true. Validation currently compares the caller-supplied current digest with the authorization-bound digest, allowing reproduction of the same digest without proving live precondition satisfaction.

Acceptance therefore remains blocked until precondition evidence is produced by a trusted evidence source and validated against live state/target. Timestamp normalization/validation must also be made explicit before relying on lexicographic expiry comparison.


### E7.76 trusted evidence implementation — 2026-09-25

The authorization branch now models precondition evidence as an immutable `PreconditionEvidence` object with:
- trusted source identity;
- target revision;
- evidence revision;
- observed conditions;
- provenance;
- canonical digest.

Authorization issuance requires trusted evidence, requires its target revision to match the authorized target, and requires all declared preconditions to be observed. Execution validation recomputes the evidence digest and rejects stale/wrong-target/unsatisfied evidence. A trusted-source allowlist is enforced.

New regression coverage includes forged source rejection and stale evidence rejection.

This closes the prior “hash of declaration is not evidence” gap at the source-contract level. Runtime CI remains the acceptance gate.


### E7.76 full re-audit — trust-boundary blockers remain — 2026-09-25

After the timestamp contract and test-call-site correction, two deeper blockers remain:
1. `PreconditionEvidence` is caller-constructible; the `source_id` allowlist authenticates only a string label, not the authority that produced the evidence.
2. `current_target_revision` remains caller-supplied; equality with the authorization-bound revision does not prove that it is the live target revision.

These require trusted evidence/target-state resolution or independently verifiable provenance. Current-head CI workflow evidence is also absent. E7.76 therefore remains unaccepted.


### E7.76 live-state resolution implementation — 2026-09-25

Execution validation no longer accepts caller-supplied `current_target_revision` or caller-supplied evidence as the authoritative execution inputs. It now resolves:
- live target revision through a `TargetRevisionResolver`;
- precondition evidence through a `TrustedEvidenceResolver`.

The validator fail-closes on resolver errors, missing evidence, target mismatch, evidence digest mismatch, or unsatisfied conditions. Tests were migrated to the resolver contract and include live-target advance rejection.

This is a boundary/API correction, not yet proof that the production wiring is trusted. Acceptance still requires verification that the runtime supplies trusted resolvers and that callers cannot inject arbitrary resolver implementations, plus CI/runtime evidence.


### E7.76 runtime-wiring audit — 2026-09-25

Runtime audit of the authorization branch shows the new resolver API is not yet wired into a trusted production execution path. `validate_execution_request` accepts arbitrary callable resolver arguments; no production caller was found that binds these resolvers to a protected evidence store and live target-state provider.

The existing `gnosis/self_learning/execution.py` still routes actual Core mutation through `SQLiteExecutionCommitAdapter` / the older `gnosis.reflection.authority.ExecutionAuthorization` boundary. That older authority path still raises `NotImplementedError` for the trusted owner-authority issuer. Therefore E7.76 must not be marked end-to-end complete.

Required next work:
1. create a non-injectable runtime execution context/provider owned by the trusted execution boundary;
2. bind target-state and evidence resolution inside that context;
3. connect E7.76 authorization validation to the actual execution entrypoint;
4. add adversarial tests proving caller-controlled resolver injection cannot bypass authorization;
5. run CI/runtime evidence on the integrated path.


### E7.76 / Core-authority boundary clarification — 2026-09-25

Runtime inspection confirms E7.76 collaboration authorization and Core mutation authorization are different boundaries and must not be merged by convenience.

- E7.76 authorizes external/public collaboration actions (publish, issue/PR, partner package, invitation, repository metadata).
- `gnosis.reflection.authority.ExecutionAuthorization` governs Core mutation and deliberately remains fail-closed pending the real owner-authority issuer.
- `gnosis.self_learning.execution.execute_approved_core_proposal()` currently invokes the Core commit adapter but does not establish an E7.76 collaboration authorization context.

Therefore the next implementation must NOT simply inject E7.76 into Core mutation. Instead:
1. define a trusted runtime context for E7.76 external-action execution;
2. bind trusted target/evidence providers inside that context;
3. add a dedicated external-action execution entrypoint that validates E7.76 before side effects;
4. keep Core mutation behind its separate owner-authority boundary;
5. add cross-boundary tests proving an E7.76 authorization cannot grant Core mutation authority and Core authorization cannot be substituted for E7.76 external-action authorization.


### E7.76 trusted collaboration runtime — 2026-09-25

Added `gnosis.self_learning.collaboration_runtime.TrustedCollaborationRuntime` as the dedicated external-action execution boundary. The runtime owns the target/evidence resolvers and the external side-effect callable; request callers cannot pass alternate resolvers through `execute()`.

The runtime calls E7.76 validation first and raises a fail-closed `PermissionError` before any external action when authorization, live target, or trusted evidence is invalid. Regression tests prove denial occurs before side effects and successful side effects occur only after authorization.

Important limitation: Python composition is not a cryptographic security boundary. Production acceptance still requires the composition root to construct this runtime from trusted providers and no untrusted path to replace the runtime object. This is now an explicit integration requirement rather than hidden in the authorization function.


### E7.76 composition-root implementation — 2026-09-25

Added `gnosis.self_learning.collaboration_entrypoint` as the explicit application composition boundary. Request execution receives only the immutable `CollaborationComposition`; target/evidence providers and the external side-effect capability are bound when the composition is created and are not parameters of request execution.

Added regression coverage for successful execution after validation and rejection of unexpected provider-injection parameters. The repository CI workflow runs pytest on Python 3.11 and 3.12 for pull requests, but this branch still requires an actual CI run before acceptance.


### E7.76 entrypoint/repository drift audit — 2026-09-25

End-to-end search identified a repository drift that must be resolved before E7.76 acceptance:

- Main currently contains `gnosis/self_learning/collaboration_execution_authorization.py`, an older E7.76-style authorization API (`issue_authorization` / `authorization_valid`) separate from the new `collaboration_authorization.py` + `collaboration_runtime.py` path.
- The current E7.76 contract branch does not contain that legacy module, so the two implementations are not currently the same runtime path.
- The repository also contains delivery authorization/manifest/receipt layers (E7.63/E7.69/E7.70) and a documented external-collaboration execution chain (E7.77+). Search did not find a concrete external-action caller wired to the new TrustedCollaborationRuntime.

Required closure:
1. establish one canonical E7.76 authorization implementation;
2. explicitly classify/archive/remove the legacy duplicate from the canonical branch rather than allowing two authority APIs;
3. identify or implement the real external-action adapter entrypoint;
4. connect adapter → CollaborationComposition → E7.76 → action → E7.77 evidence/reconciliation;
5. add a static/architectural regression proving no external action bypasses the composition boundary;
6. update STATUS.md from stale repository/branch wording to the actual canonical repository and current contract state before acceptance.


### E7.76 integration-base audit — 2026-09-25

Current PR #74 head `b29c4f8` is 539 commits behind `main` and diverged; its 20 commits are based on an older merge base. This makes the branch unsuitable as an integration proof until reconciled with current main.

PR review comment recorded: review_id 5320827781.

Acceptance blockers reaffirmed:
- reconcile branch with current main and re-audit;
- remove/classify duplicate E7.76 authority implementation;
- wire a real production external-action adapter through the composition root;
- prove E7.76 → side effect → E7.77 evidence/reconciliation;
- add bypass regression coverage;
- produce current CI/runtime evidence and synchronize STATUS.md.


### E7.76 current-main reconciliation — 2026-09-25

A fresh integration branch `e7-76-current-main-reconciliation` was created directly from current `main` rather than force-updating the old divergent PR branch.

Canonical E7.76 implementation on this branch:
- `gnosis/self_learning/collaboration_authorization.py`
- `gnosis/self_learning/collaboration_runtime.py`
- `gnosis/self_learning/collaboration_entrypoint.py`

The older `gnosis/self_learning/collaboration_execution_authorization.py` and its obsolete test were removed from this integration branch to prevent dual authority APIs.

The original PR #74 branch remains untouched because it is 539 commits behind current main. It must not be treated as the integration candidate.

Next gate: inspect all current-main imports/usages and CI for the canonical API, then wire the real external adapter and E7.77 evidence path.


### Current-main dependency audit + adjacent defect cleanup — 2026-09-25

Current-main tree inspection after reconciliation shows no remaining `collaboration_execution_authorization.py` file in the canonical branch tree; the old module is therefore no longer part of the integration candidate. Generic `authorization_valid` occurrences in recovery code are unrelated parameters/guards, not imports of the removed E7.76 authority API.

The audit also found a separate duplicate definition of `validate_delivery_build_binding()` in `gnosis/self_learning/delivery.py`. Removed the duplicate definition without changing the surviving function's behavior.

The reconciled tree already contains E7.77 execution evidence, E7.78 collaboration recovery, E7.79 incident resolution, and lifecycle closure modules, but these remain contract components rather than a proven end-to-end adapter path from E7.76 side effect to E7.77 evidence.

Next gate remains real external adapter discovery/wiring plus cross-contract integration tests.
