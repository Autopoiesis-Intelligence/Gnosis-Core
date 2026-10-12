# SEQ 40 — Main handoff reconciliation proposal

**Date:** 2026-10-12  
**Status:** PROPOSAL ONLY — documentation scope; not an authorization to merge or implement Memory  
**Canonical repository:** `Autopoiesis-Intelligence/Gnosis-Core`  
**Observed main HEAD for this review:** `0daf9cfdfac673972796066ca809f38f204c1a16`

## Purpose

Define the smallest coherent reconciliation for the canonical handoff documents. This proposal is kept on recovery branch `recovery/working-state-2026-10-12`; it does not edit the canonical `main` files and does not establish that the recovery branch is safe to merge.

## Evidence and conflicts to resolve

1. On the observed `main` snapshot, `AI_CONTEXT.md` and `docs/PROJECT_STATE.json` still identify `Mikhail-Kucheriavyi-23/Gnozis-V2`, not the canonical repository above.
2. The observed `main` project-state snapshot pins `canonical_head` to `7d40a9c91fd2e69736305141a71b62aeebb99461`, while the live `main` HEAD observed for this review was `0daf9cfdfac673972796066ca809f38f204c1a16`. A pinned SHA is a snapshot, never a live pointer; it must be rechecked at every session.
3. The observed `main` project state says to proceed to an “already approved Memory corrective pass” after a read-only audit, while the active phase ledger forbids Memory corrective implementation. The ledger's “Next gate sequence” also places Memory corrective pass next despite that forbidden scope. Neither sequencing sentence is sufficient authority to start implementation.
4. The active recovery state correctly records the independent reviewer as `NOT_ASSIGNED`. ChatGPT self-review can be a bounded review, but is not independent verification.
5. The observed main handoff protocol's minimum recovery set does not lead with the machine-readable `docs/PROJECT_STATE.json`, and directs new sessions to legacy role/strategy documents whose assumptions may not reflect the current working model. The protocol should make live-ref and scope reconciliation mandatory before any task is started.

## Proposed minimal changes (not applied to main)

### A. `AI_CONTEXT.md`

- Replace the old repository identity/link with `Autopoiesis-Intelligence/Gnosis-Core`.
- State that any displayed SHA is a dated observation, not a live pointer.
- Direct every new session to fetch current `main` and compare it with the project-state snapshot before treating any phase, status, or next action as current.
- Preserve unknowns as `UNKNOWN` / `UNVERIFIED`; do not turn a prior report into current evidence.

### B. `docs/PROJECT_STATE.json`

- Keep the canonical repository as `Autopoiesis-Intelligence/Gnosis-Core`.
- Store `canonical_head` only as the exact observed SHA for the update that writes the file; retain the existing staleness rule requiring a live comparison at each new session.
- Keep `independent_reviewer` as `NOT_ASSIGNED` unless a genuinely independent reviewer is explicitly assigned.
- Replace any wording that presumes Memory corrective work is already approved with: “Finish documentation-only reconciliation; recheck the live main SHA and exact-head evidence; then select only a task permitted by the active phase ledger. Memory implementation remains forbidden until the phase is formally changed and explicit owner authorization is recorded.”
- Keep the allowed/forbidden scope consistent with `docs/PHASE_LEDGER.md`.

### C. `docs/PHASE_LEDGER.md`

- Keep the current phase at `CONTEXT-CONTINUITY ARCHITECTURE` / `DOCUMENTATION_AND_ARCHITECTURE` unless the owner explicitly records a phase transition.
- Keep Memory corrective implementation in `Forbidden scope`.
- Replace the contradictory “Next gate sequence” that lists Memory corrective pass as the immediate next phase step with a sequence that ends at a decision gate: documentation/state reconciliation → live-head and evidence recheck → owner selects a task within the active phase or explicitly authorizes a formal phase transition. No Memory implementation is implied.
- Keep `NOT ASSIGNED` for the independent reviewer. Do not label ChatGPT review independent.

### D. `docs/AI_HANDOFF_PROTOCOL.md`

- Make `docs/PROJECT_STATE.json` and `docs/PHASE_LEDGER.md` the first required recovery inputs, followed by `AI_CONTEXT.md`, `STATUS.md`, and this protocol; treat strategy/role documents as supporting context that must be reconciled against the active phase rather than automatically authoritative.
- Before work, fetch live `main`, record exact branch/HEAD, compare the project-state `canonical_head`, and report any delta. If the pin is stale or documents conflict, mark the conflict `RECONCILIATION REQUIRED` and perform read-only reconciliation first.
- Add an explicit rule: no “next permitted action” string can override a phase's forbidden scope; a phase transition and implementation authorization must be explicit and durable.
- Retain the distinction among implementation, verification, and acceptance, and the rule that connector access does not confer architectural authority.

## Acceptance checks for a later implementation of this proposal

- [ ] All four documents name the same canonical repository.
- [ ] The observed SHA is labelled as a snapshot and the mandatory live comparison is explicit.
- [ ] `PROJECT_STATE.json` and `PHASE_LEDGER.md` agree on phase, reviewer assignment, allowed scope, forbidden scope, and next action.
- [ ] No document implies that Memory implementation is authorized while the active phase forbids it.
- [ ] Handoff recovery reads machine-readable state and verifies live refs before execution.
- [ ] Diff is documentation-only; no runtime, Core semantics, Memory, identity/auth, encryption, Bridge, federation, schema, migration, or workflow changes.
- [ ] Exact-head CI and other relevant checks are reported for the resulting commit without transferring prior-head results.

## Explicit non-goals

This proposal does not authorize changing `main`, merging/rebasing PR #169, implementing Memory, changing runtime/schema/migrations/workflows, or claiming CI/runtime acceptance. PR #169 remains Draft/open/unmerged until separate ancestry, baseline, and exact-head verification gates are satisfied.
