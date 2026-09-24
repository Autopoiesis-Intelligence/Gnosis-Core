# E8.28 — Durable Partner Learning Recovery Verification

Status: PARTIAL / UNVERIFIED.

E8.28 verifies that a committed partner learning result survives database close/reopen and that canonical durable-graph verification detects audit tampering.

The recovery path reuses `connect`, `verify_durable_graph`, `recover_instance` and `load_evolution_memory`; it creates no recovery-side state model.

Acceptance requires exact runtime/CI evidence. Memory deletion is treated as loss of learning evidence, not reconstructed or silently fabricated.