# Continuation Reconciliation — 2026-10-12

## Purpose

Provide one bounded, evidence-based recovery note for the current canonical repository. This note records conflicts among older handoff documents; it does not silently rewrite their historical content or authorize implementation work.

## Live baseline observed for this sequence

- Canonical repository: `Autopoiesis-Intelligence/Gnosis-Core`
- Branch inspected: `main`
- Main SHA observed: `00648d14106de03e194c58d90790d2fe202670a4`
- Active phase in `docs/PHASE_LEDGER.md`: `CONTEXT-CONTINUITY ARCHITECTURE`
- Phase status: `DOCUMENTATION_AND_ARCHITECTURE`

The SHA above is a point-in-time observation. Re-fetch the live branch before using it as current evidence in a later session.

## Conflicts requiring reconciliation

1. `docs/PROJECT_STATE.json` identifies `Mikhail-Kucheriavyi-23/Gnozis-V2` and pins `7d40a9c91fd2e69736305141a71b62aeebb99461`. That identity and pin do not match the canonical repository and main SHA observed above.
2. `AI_CONTEXT.md` also identifies the older `Mikhail-Kucheriavyi-23/Gnozis-V2` repository.
3. `STATUS.md` identifies `Mikhail-Kucheriavyi-23/Genezis` and contains older dated status material. It must not be treated as a live current-head report without reconciliation.
4. `docs/PHASE_LEDGER.md` keeps the active phase documentation-only and forbids Memory corrective implementation. Although it lists Memory corrective work after the context-continuity audit, that is a future gate, not permission to skip the audit or to begin implementation now.
5. `docs/CONTEXT_IMPLEMENTATION_TASK.md` describes a bounded TaskContext runtime scope, while `docs/CONTEXT_IMPLEMENTATION_GAP_R1.8.2.md` records that the implementation gap remains. PRs #159 and #170 are separate proposals with failing full CI evidence recorded in their PR metadata; neither is acceptance evidence for the complete continuity layer.
6. Task Checkpoint storage direction B is a preference to use an application-provided connection. The inspected source has not established a production composition root/provider or a canonical immutable accepted checkpoint source. That track remains blocked.

## Authority and evidence rules

When recovery documents disagree:

1. Re-check the live repository and exact branch HEAD.
2. Treat current source and reproducible runtime/CI evidence as stronger than snapshots, handoff notes, PR descriptions, or conversation memory.
3. Use `UNKNOWN` when the current state cannot be established; use `CONFLICT` when authoritative candidates disagree.
4. Do not infer architecture or implementation authority from connector access, an old task specification, or a stale `next_permitted_action` field.
5. Keep implementation, verification, and acceptance as separate states.

## Next permitted action

Perform a documentation-only reconciliation of the canonical identity, current-head/staleness rules, and phase/status pointers. Do not modify Core, Memory, identity/authentication/authorization, runtime schema, migrations, or production connection paths. Do not merge PRs or claim acceptance. After reconciliation, re-check exact-head CI and decide the next bounded task from the active phase ledger.

## Change/evidence record

- This file is a recovery/reconciliation note, not proof that any runtime behavior works.
- No runtime, Core, Memory, schema, database path, or migration change is authorized by this note.
- The creation commit and its branch/PR state must be checked from live GitHub metadata.
