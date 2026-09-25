[object Object]

### P0 recovery-authorization audit — 2026-09-25

Audit result: the current `recover_instance(conn, instance_id)` path performs `verify_durable_graph(conn)` and then loads the instance. No explicit authorization token, governance decision, capability, or authorization state is required by this recovery entry point, and no recovery authorization event is bound to the recovery operation.

This is an **OPEN contract gap**, not a defect to patch opportunistically. Adding an arbitrary actor parameter would not constitute authorization. The correct fix belongs to the Governance/Recovery contract and must define the authority source, allowed states, audit binding, and fail-closed behavior first.

P0-R2 therefore remains open with:
- integrity verification: substantially covered;
- replay/idempotency: bounded and regression-tested;
- recovery authorization: MISSING contract/evidence;
- current-main CI/runtime evidence: MISSING.
