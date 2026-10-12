# ADR: Canonical Task Checkpoint Resolution

**Status:** Proposed architecture decision  
**Phase:** CONTEXT-CONTINUITY ARCHITECTURE  
**Baseline:** `Autopoiesis-Intelligence/Gnosis-Core@00648d14106de03e194c58d90790d2fe202670a4`  
**Scope:** Read-only contract for resolving the canonical continuation checkpoint. No schema, database path, or runtime implementation is assigned by this ADR.

## Context

The repository defines an immutable `TaskCheckpoint` as the durable continuation unit and a Context Snapshot as a derived transport/read model. A `TaskContextRepository` and related model code exist, but current repository evidence does not identify an accepted live checkpoint record and canonical production database/path. Existing tests against in-memory or temporary databases do not establish a production source.

The snapshot MVP must therefore not infer the current task from chat history, stale status files, an arbitrary SQLite database, or a mutable repository record.

## Decision

A Context Snapshot resolver MUST consume a checkpoint only from a source explicitly designated as canonical by a separately accepted architecture/implementation decision. Until that source and its read interface are designated, task-level fields that cannot be grounded remain `UNKNOWN`; conflicting candidate sources are reported as `CONFLICT`.

This ADR defines resolution semantics only. It does not designate the existing TaskContext repository as the canonical checkpoint store, choose a database path, add tables, or authorize Core/Memory/Identity changes.

## Resolution contract

Given an explicit `task_id`, a conforming read resolver MUST:

1. Resolve the task from the designated canonical task source; do not discover tasks by scanning arbitrary files or databases.
2. Retrieve checkpoint records associated with that exact task identity and source.
3. Consider only checkpoints that are immutable after publication and whose acceptance was explicitly recorded by the project integration gate.
4. Select the latest accepted checkpoint using the source's documented monotonic sequence for that task. Creation timestamps alone are not an ordering authority.
5. Verify that the selected checkpoint's task identity, checkpoint identity, sequence, baseline reference, and required provenance fields are internally consistent.
6. Return immutable evidence references and the checkpoint's implementation, verification, and acceptance states as separate dimensions.
7. Build a Context Snapshot as a read model only. Snapshot generation must not create a checkpoint, increment a sequence, change acceptance, or mutate canonical state.
8. Report missing source/record as `UNKNOWN`; report multiple incompatible candidates, duplicate sequence numbers, broken lineage, or contradictory acceptance records as `CONFLICT`. Never silently choose one.
9. Preserve the source identity and exact checkpoint identifier in snapshot provenance so the result can be traced back to its origin.
10. Operate read-only. A recovery request must not initialize application/Core schema, migrate a database, or create project state as a side effect.

## Freshness and evidence rules

- The checkpoint is the workflow-continuity authority only after its canonical source is explicitly designated and its acceptance is evidenced.
- Repository branch/HEAD and CI status are independently refreshed observations. A checkpoint that names a baseline does not prove that the baseline is current or that CI passed.
- Evidence references must identify observable artifacts (for example, commit SHA, workflow run URL/ID, report artifact or accepted contract). A free-form status label such as `PASS` is not evidence.
- A referenced artifact's existence and its relationship to the checkpoint are separate from whether the artifact proves the claim. Consumers must preserve this distinction.
- If the repository has advanced beyond the checkpoint baseline, expose that difference; do not silently rewrite the checkpoint or describe it as current.
- Conversation history, AI-generated transfer notes, `STATUS.md`, and unstructured context files may be presented as non-authoritative observations, but must not override the canonical checkpoint.

## Required resolver result

The logical result (not a prescribed serialized schema) must make these dimensions distinguishable:

- resolution outcome: `RESOLVED`, `UNKNOWN`, or `CONFLICT`;
- canonical source identifier and source version/ref;
- task ID, checkpoint ID, and monotonic sequence;
- checkpoint baseline reference;
- implementation state;
- verification state;
- acceptance state and its recorded integration-gate evidence;
- evidence references and provenance;
- freshness comparison against the live repository when applicable;
- unresolved conflicts and the next permitted read-only action.

A partial result may be returned when some dimensions are unknown, but unknown values must remain explicit.

## Non-goals

This decision does not define SQLite DDL, a migration, repository API signatures, task creation, authentication/authorization, capability enforcement, Core transitions, Memory behavior, or autonomous execution. Those require their own authorized bounded task and verification.

## Acceptance checks for a future implementation task

The implementation task must test at least:

1. no designated source → `UNKNOWN`, with no files or schema created;
2. one accepted immutable checkpoint → deterministic resolution;
3. newer unaccepted checkpoint → older accepted checkpoint remains the latest accepted one;
4. same task with duplicate sequence or incompatible accepted candidates → `CONFLICT`;
5. checkpoint for another task cannot be selected;
6. missing or contradictory acceptance evidence fails closed;
7. stale repository baseline is surfaced without rewriting checkpoint state;
8. evidence references and provenance survive snapshot serialization;
9. resolver is read-only and idempotent;
10. snapshot output cannot mutate task/checkpoint state.

## Consequence / next gate

The next architecture gate is to identify and explicitly accept the canonical source and its read interface using repository evidence. Only then may a separate bounded implementation task wire the snapshot to that source. Until that gate is met, the existing snapshot MVP is a repo identity/phase diagnostic, not a complete task-continuity handoff.

## Related contracts

- `docs/TASK_PROPOSAL_PERSISTENCE_MODEL.md`
- `docs/CONTEXT_SNAPSHOT_CONTRACT.md`
- `docs/TASK_CONTEXT_CONTINUITY_CONTRACT.md`
- `docs/PHASE_LEDGER.md`


## Repository evidence at the baseline

Inspection of `main` at `00648d14106de03e194c58d90790d2fe202670a4` found:

| Artifact | Observed property | What it establishes |
|---|---|---|
| `gnosis/context/model.py` | Defines frozen `TaskContext`; no `TaskCheckpoint` type | A context value object exists, not the immutable checkpoint entity specified by the persistence model |
| `gnosis/context/repository.py` | `TaskContextRepository` creates `task_contexts` via `executescript(CONTEXT_SCHEMA)`; supports revisioned updates | A mutable context repository exists; it is not evidence of an accepted immutable checkpoint store |
| `gnosis/context/handoff.py` | Builds a `ContextHandoff` from a `TaskContext` | A handoff projection exists, but it does not resolve the latest accepted checkpoint |
| `docs/TASK_PROPOSAL_PERSISTENCE_MODEL.md` | Defines conceptual Task and immutable Task Checkpoint fields; says exact DDL/API is a separate implementation task | Checkpoint persistence is specified conceptually, not established as implemented by this contract |
| `docs/CONTEXT_SNAPSHOT_CONTRACT.md` | Defines snapshot as derived from the latest checkpoint | Establishes the intended authority relationship, not a live source or production path |

No repository evidence in this inspection identifies a canonical production database path, an accepted checkpoint record, a monotonic checkpoint sequence implementation, or an integration-gate acceptance record for such a checkpoint.

**Current source-selection outcome: `UNKNOWN` / not yet implementable without an explicit architecture decision.** The logical authority is the Task Checkpoint concept from the persistence model, but no concrete implemented source may be designated from the evidence above. Do not treat `TaskContextRepository` as a substitute and do not add a second schema as a workaround.

## Decision gate before wiring a resolver

The source-designation task must provide evidence for all of the following before an adapter is implemented:

1. Canonical source artifact and ownership boundary.
2. Exact storage/repository location and initialization lifecycle.
3. Task identity lookup and accepted-checkpoint query contract.
4. Immutable checkpoint publication and monotonic per-task ordering.
5. Explicit acceptance record and the gate that produces it.
6. Read-only access path that does not initialize or mutate Core/application state.
7. Compatibility/migration strategy, if existing persistence is to be extended.
8. Tests against a real persisted checkpoint and a missing-source/no-side-effect case.

If any item remains unassigned, keep the snapshot's task-level state `UNKNOWN` and report the missing decision rather than guessing.
