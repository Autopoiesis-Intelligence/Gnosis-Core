# R1.9 — State/Evolution Repository Contracts

## Extracted canonical path

The existing implementation already defines the real contract more precisely than the provisional port:

`save_state` / `load_state`
→ immutable State persistence + content/hash reconciliation.

`save_candidate` / `load_candidate`
→ candidate binds parent state to proposed state.

`persist_transition`
→ atomic candidate + transition + audit + accepted-head update.

`load_transition_records` / `verify_durable_graph`
→ recovery and continuity verification.

`transition_id`
→ deterministic transition identity.

## Contract separation

### StateRepository

Minimum semantic operations:

- save_state(state)
- load_state(state_id)
- save_candidate(candidate)
- load_candidate(candidate_id)

Invariant: persisted identity must reconcile with reconstructed object identity.

### EvolutionRepository

Minimum semantic operations:

- persist_transition(instance, candidate, record, actor, failure_at=None)
- load_transition_records(instance_id=None)
- verify_durable_graph()
- recover_instance(instance_id)

Invariant: an accepted transition must preserve source-head continuity and durable provenance.

### AuditRepository

The existing `append_audit` / `verify_audit_chain` form a separate semantic capability.

Audit evidence must remain append-only and hash-linked.

## Important discovery

There is no existing `save_transition()` function. The real atomic operation is `persist_transition()`.

Therefore the provisional SQLite adapter created earlier must not be used as a compatibility claim for a nonexistent API. It will be replaced by capability-specific adapters after contract tests are established.

## Transaction boundary

`persist_transition()` already owns the atomic sequence:

1. begin transaction;
2. reload database instance/head;
3. verify candidate/source binding;
4. save candidate;
5. insert transition;
6. append audit event;
7. update instance head if accepted;
8. commit;
9. injected failure points verify rollback behavior.

This sequence is part of the semantic contract and must not be weakened during migration.

## Migration rule

The new port must describe this semantic operation, not expose raw SQL and not reduce it to generic CRUD.

Next step: replace the provisional broad persistence port with `StateRepository` and `EvolutionRepository` contracts matching these semantics, then write contract tests against the current SQLite implementation.
