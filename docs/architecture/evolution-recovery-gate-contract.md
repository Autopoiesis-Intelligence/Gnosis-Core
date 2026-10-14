# Evolution Recovery Gate Contract

Status: DESIGN / NOT IMPLEMENTED
Scope: integration between `run_reflection_gate()` and `recover_evolution_audit()`.
Branch context: security/signed-owner-auth-commit-boundary-2026-10-14

## Current observed contract

`run_reflection_gate()` receives instance-recovery authorization, an instance ID, and a timestamp. When the database contains evolution provenance, it calls `recover_evolution_audit(conn)` without a provenance ID, observations, proposed state, or evolution-recovery authorization.

`recover_evolution_audit()` requires a provenance identity for trusted recovery and independently supplied observations and proposed state. It also defaults to rejecting recovery unless authorization is explicitly valid. Therefore, the current call cannot prove evolution recovery and must fail closed. Instance-recovery authorization must not be silently reused as evolution-recovery authority.

## Required integration contract

Before implementation, the caller and API must explicitly bind all of the following:

1. **Selection scope** — an explicit provenance ID or a defined, deterministic set of provenance IDs to verify. Never choose an arbitrary first row.
2. **Evidence inputs** — observations and proposed state supplied by an identified trusted source, with digests/content identity checked against the selected persisted record.
3. **Authorization domain** — authorization appropriate to evolution recovery, bound to the selected provenance and evidence scope. Do not convert a boolean, instance authorization, or caller assertion into trusted authority.
4. **Integrity result** — `verified`, `tampered`, and `legacy_unverified` remain distinguishable. Only `verified` may satisfy trusted recovery.
5. **Failure semantics** — missing, ambiguous, mismatched, expired/revoked, or legacy-unverified inputs fail closed with a stable reason. A reflection artifact must not imply that evolution recovery passed when it was not performed.
6. **Compatibility** — legacy rows remain readable, but must not be silently backfilled or promoted to verified without independent evidence and an explicit migration policy.

## Non-goals

- Do not change `provenance_id` or `evolution_identity` semantics to include lifecycle status.
- Do not introduce a second authorization system or bypass the existing trusted-owner / execution-authorization boundary.
- Do not treat a digest stored beside mutable data in the same SQLite database as an external trust anchor.
- Do not make the gate pass merely because recovery was skipped or because no exception was raised.

## Acceptance tests required before implementation is considered complete

- A valid, explicitly selected provenance record with independently supplied matching evidence and valid evolution-recovery authorization can be verified.
- A missing or ambiguous provenance selection fails closed.
- Tampered status, evidence, identity, or audit linkage fails closed.
- A legacy row with no status digest remains `legacy_unverified` and cannot satisfy trusted recovery.
- Instance-recovery authorization alone does not authorize evolution recovery.
- The reflection gate reports success only when every required trust domain has actually passed.
- Existing instance-only gate behavior remains unchanged when no evolution provenance exists.

## Implementation sequence

1. Identify the authoritative producer/source for provenance selection, observations, and proposed state.
2. Identify the existing authorization type and issuance path suitable for this exact evolution-recovery scope; if none exists, document the gap rather than inventing authority.
3. Define the narrowest typed input contract and stable failure reasons.
4. Implement the binding and tests together.
5. Validate exact-head CI, Import Graph, CodeQL, and Dependency Review separately. Do not call the overall check set green while any required check fails.

## Evidence note

This document records a design constraint, not an implementation claim. At the time of writing, the integration gap is observed in `gnosis/reflection/gate.py` and `gnosis/evolution/recovery.py`. No runtime or CI proof is implied by this document.
