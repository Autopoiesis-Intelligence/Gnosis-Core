# E8.27 — Runtime Bridge: Admission to Canonical Persistence

Status: PARTIAL / UNVERIFIED.

E8.27 closes the runtime gap identified by E8.22: an admitted partner learning candidate is explicitly bound to the E8.23 request and then persisted through E8.26.

Required bindings are result ID, provenance/candidate digest and evidence references. Admission must be commit-authorized and the request must be READY_FOR_CANONICAL_COMMIT.

The bridge creates no execution authority and no second persistence model. Final durability remains the canonical SQLite/EvolutionMemory/audit boundary.

Acceptance requires exact runtime/CI evidence and recovery verification.