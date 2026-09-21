# R1.9 — Persistence Topology Map

## Result

Persistence is not one subsystem. It is a set of related stores sharing one SQLite connection and transaction boundary.

### Canonical durable state path

`gnosis/storage/database.py`
→ connection/schema/transaction primitive

`gnosis/storage/repositories.py`
→ states / relations / candidates / instances / transitions / audit_events / evolution_memory

This is the primary durable Core path.

### Evolution evidence path

`gnosis/evolution/transaction.py`
→ evolution provenance + evolution audit

This is a second persistence family on the same database connection. It must not become a second state authority.

### Reflection path

`gnosis/reflection/persistence.py`
→ reflection reports/evidence/audit-related records

`gnosis/reflection/authority_persistence.py`
→ authority request records

These records describe analysis/governance evidence. They do not define Ψ state.

### Context path

`gnosis/context/repository.py`
→ task context records

This is runtime context, not canonical Ψ state and not the Development Archive.

## Critical architectural correction

The first proposed `PersistencePort` was too small and incorrectly assumed a single generic persistence API could represent all existing semantics.

It is therefore **not promoted as an active integration boundary yet**.

The correct boundary must separate semantic capabilities:

1. StateRepository
2. EvolutionRepository
3. Audit/EvidenceRepository
4. ReflectionRepository
5. AuthorityRepository
6. ContextRepository

All may share one physical SQLite connection/transaction infrastructure while remaining semantically distinct.

## Why this matters

A single broad `PersistencePort` would hide important trust boundaries and could make reflection, context or audit data appear equivalent to canonical state.

The new architecture must preserve distinctions rather than merely abstracting SQLite.

## Migration decision

Keep the existing storage implementation in place.

Replace the provisional broad port with capability-specific contracts after the exact method sets are extracted from the existing repositories.

Do not physically move storage yet.

## Next step

Extract the minimum method contracts for `StateRepository` and `EvolutionRepository` first, because they define the canonical state → candidate → transition persistence path.
