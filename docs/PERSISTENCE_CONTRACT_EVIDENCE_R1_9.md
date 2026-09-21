# R1.9 — Persistence Contract Evidence Matrix

## Existing executable evidence

The current repository already has substantial tests for the exact semantic contracts required by the migration.

### State / instance durability

`tests/test_persistence.py`
- root round-trip preserves state identity;
- accepted transition advances the head;
- rejected transition does not advance the head;
- foreign-key constraints reject orphan state references;
- schema version incompatibility fails closed.

### Atomic evolution

`tests/test_persistence_hardening.py`
- fault injection at transaction stages rolls back correctly;
- post-commit failure leaves the committed transition durable;
- restart recovery preserves budget/history;
- unauthorized head movement is detected by durable-graph verification.

### Replay / identity

`tests/test_transition_replay_idempotency.py`
- identical transition replay is idempotent;
- conflicting replay is rejected.

`tests/test_transition_identity_integrity.py`
- transition identity tampering is detected;
- transition identity is deterministic.

### Transition ↔ audit linkage

`tests/test_transition_audit_link_integrity.py`
- valid persisted transition/audit linkage verifies;
- tampered linkage is rejected.

### Audit chain

`tests/test_persistence.py` and related audit tests cover:
- append-only behavior;
- hash mismatch detection;
- previous-hash tampering;
- sequence tampering;
- inserted-middle-event detection.

## Migration conclusion

The semantic persistence contract is already strongly represented by executable tests.

Therefore the next safe action is **not** to add a second set of duplicate behavior tests. Instead, extract contract fixtures/helpers and make the existing SQLite implementation satisfy explicit capability protocols.

## Acceptance gate

The architecture migration may not remove or weaken any of the above evidence.

After adapter extraction, the same tests must remain green or equivalent contract tests must prove the same invariants.

## Next step

Create capability-specific protocols and an adapter facade over the current repositories without changing persistence semantics:

- `StateRepository`
- `EvolutionRepository`
- `AuditRepository`

Do not yet migrate Reflection, Authority or Context persistence.
