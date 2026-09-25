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
