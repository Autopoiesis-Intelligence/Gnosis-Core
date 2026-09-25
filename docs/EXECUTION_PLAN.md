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
