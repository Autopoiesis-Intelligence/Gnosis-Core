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


## SEQ 19 — Source-design alternatives and bounded recommendation

The related persistence model already resolves the **logical authority**: the immutable Task Checkpoint is the canonical task-continuation record; Context Snapshot is derived from it. The remaining blocker is not which concept is authoritative, but the absence of an implemented, accepted storage/read path.

### Alternatives evaluated against existing contracts

| Option | Fit with repository contracts | Decision |
|---|---|---|
| A. Add a Task-layer persistence boundary with immutable `task_checkpoints`, explicit acceptance records, and read-only lookup by `task_id` | Matches the persistence model's additive Task layer and immutable checkpoint contract without introducing a second Core State model | **Preferred architecture direction; not yet approved as a concrete storage implementation** |
| B. Treat `TaskContextRepository` / `task_contexts` as the checkpoint source | Repository supports mutable revisioned updates and initializes its schema in the constructor; no accepted immutable checkpoint record or monotonic checkpoint sequence was evidenced | **Rejected as the canonical checkpoint source** |
| C. Reuse Core state/transition tables as task checkpoints | Persistence model explicitly separates user/task entities from Core state and prohibits a second/reinterpreted State model; no contract establishes Core transitions as task checkpoint acceptance | **Rejected absent a separate architecture decision** |
| D. Infer the source from a database file, status document, chat history, or arbitrary existing persistence | No stable source designation or acceptance authority; risks selecting stale or non-authoritative state | **Rejected** |

### Recommended next bounded decision

Accept Option A only at the **logical architecture level**: task checkpoints belong to an additive Task persistence boundary, are immutable after publication, have a monotonic per-task sequence, and carry explicit acceptance evidence. Do not yet prescribe a database path, DDL, migration, repository API, or constructor lifecycle.

Before runtime implementation, a separate task must inspect the repository's existing Persistence configuration and lifecycle and propose the narrowest compatible location for this Task-layer boundary. It must state whether the Task layer can extend an existing configured persistence backend without creating an independent Core State store. That proposal must include migration/compatibility and read-only recovery implications and must be explicitly accepted before code changes.

### Exit criteria for this architecture blocker

- [x] Logical authority identified from existing persistence/snapshot contracts: immutable Task Checkpoint.
- [x] Mutable `TaskContextRepository` shortcut ruled out.
- [x] Core-state reinterpretation and guessed-source discovery ruled out.
- [ ] Concrete persistence boundary and lifecycle evidenced in repository.
- [ ] Acceptance-record producer and monotonic sequence semantics tied to a concrete source.
- [ ] Explicit architecture approval recorded.
- [ ] Separate implementation task authorized.

**SEQ 19 result:** architecture options narrowed; implementation remains blocked. No runtime or CI claim is implied by this documentation update.


## SEQ 20 — Existing Persistence lifecycle inspection

**Inspection baseline:** `main` at `0a4b00a7bc810788438bf3a46bead3e4adc9944e`. This section records observed repository facts; it does not authorize schema or runtime changes.

### Existing storage boundary

| Artifact | Observed implementation | Consequence for Task Checkpoint |
|---|---|---|
| `gnosis/storage/database.py` | Exposes `connect(path=":memory:")`, `transaction(conn)`, and `close(conn)`; uses stdlib `sqlite3`; sets `foreign_keys=ON` and `busy_timeout=5000` | A shared Persistence boundary exists, but the default is an in-memory database and does not identify the production/configured path |
| `gnosis/storage/database.py` | `SCHEMA_VERSION = 5`; `connect()` may update supported v3/v4 metadata, run schema DDL, insert schema metadata, and invoke Reflection schema initialization | This connection factory is not a safe read-only recovery entry point: opening a database may mutate or initialize schema |
| `gnosis/storage/database.py` | Current schema includes Core tables such as `states`, `instances`, `transitions`, `evolution_memory`, and `audit_events` | Do not model Task Checkpoint as another Core State or reinterpret existing Core records as task acceptance |
| `gnosis/storage/repositories.py` and `gnosis/storage/__init__.py` | Repositories operate on a caller-supplied SQLite connection; package exports the connection lifecycle and Core persistence operations | An additive Task repository could conceptually share the existing connection boundary, but current evidence does not establish a Task repository, configured application composition root, or production connection provider |
| `docs/architecture/PERSISTENCE_ADR.md` | Existing Persistence ADR describes SQLite and repository-owned transaction/serialization boundaries; it also says no production code is authorized by that document | This provides a storage design precedent, not permission to extend the schema under the current phase |

### Decision implications

1. **Preferred future integration point:** an additive Task-layer repository that accepts an already-configured persistence connection from an explicitly identified composition root. It must not independently open an inferred database file, create a second Core State store, or make the snapshot CLI call the schema-initializing `connect()` as a read-only shortcut.
2. **Migration compatibility is unresolved:** adding checkpoint tables would require an explicit schema-version/migration decision because `connect()` currently owns schema initialization and version handling. Do not silently change `SCHEMA_VERSION`, `SCHEMA`, or migration behavior in this ADR task.
3. **Read-only recovery path is unresolved:** the existing `connect()` function cannot be assumed read-only. A future implementation must identify whether an existing configured connection can be opened in SQLite read-only mode without running DDL/Reflection initialization, or define another narrowly scoped read-only access contract. Test no file creation and no schema changes when the source is absent.
4. **Production path is still UNKNOWN:** the default `:memory:` argument is a function default, not evidence of the deployed database path. No physical path is selected by this ADR.
5. **Checkpoint acceptance and sequence are still missing:** current Core audit `sequence` is database-wide and is not evidence of a per-task checkpoint sequence or a project integration-gate acceptance record. Do not reuse it for Task Checkpoint ordering without a separate accepted contract.

### Narrow proposal for the next architecture gate

- Keep the logical authority as immutable Task Checkpoint in the additive Task layer.
- Before implementation, identify the real configured persistence/composition root and its connection lifecycle from actual callers/configuration.
- Propose the smallest compatible migration path and a read-only connection path that bypasses schema initialization.
- Specify immutable publication, per-task monotonic sequence, explicit acceptance evidence, and tests for missing source/no side effects.
- Require explicit architecture approval before DDL, migration, API, or runtime changes.

### SEQ 20 result

- [x] Existing SQLite persistence module and connection lifecycle inspected.
- [x] Schema initialization/migration side effects identified.
- [x] Existing Core state tables distinguished from Task Checkpoint authority.
- [ ] Real configured production connection source identified.
- [ ] Read-only no-initialization path established.
- [ ] Task acceptance-record producer and per-task sequence implemented/evidenced.
- [ ] Architecture proposal explicitly accepted; runtime implementation authorized.

**Status:** architecture recommendation only. No runtime code, schema, database path, or migration was changed by this sequence.


## SEQ 21 — Configured connection and caller search

**Inspection baseline:** `main@00648d14106de03e194c58d90790d2fe202670a4`. This is source inspection only; it does not authorize runtime changes.

### Callers and lifecycle found

- `gnosis/self_learning/partner_learning_recovery.py` defines `recover_partner_learning(path, ...)` and calls `connect(path)`. The path is supplied by its caller; this function does not resolve a configured/default production path.
- The other source-level `connect()` usage surfaced by the targeted repository search is diagnostic corpus generation, where a temporary `diagnostic.sqlite` is created. This is explicitly a disposable test/diagnostic artifact, not a production path.
- `gnosis/context/repository.py` accepts a caller-owned SQLite connection, but `TaskContextRepository.__init__()` runs `executescript(CONTEXT_SCHEMA)`; its API is not read-only. Its tests open either the default in-memory DB or a temporary test DB.
- `gnosis/context/cli.py` / `gnosis/context/snapshot.py` read repository files and Git metadata only. The snapshot CLI does not open SQLite or load persisted Task Context/Checkpoint records.
- Targeted code search found no evidence at the inspected baseline of a canonical application composition root, environment/config key for a production database path, or a no-DDL read-only database opener. Absence here is bounded to the searched source/config paths; do not generalize it into proof that no deployment-specific external configuration exists.

### SEQ 21 decision

1. **Configured connection provider: UNKNOWN / not located in inspected source.** Do not infer one from test paths or from the path parameter of a recovery helper.
2. **Existing connection reuse: technically compatible as a repository shape, but not sufficient.** Existing repositories accept `sqlite3.Connection`; the context repository initializes a mutable schema, and `connect()` runs DDL/migration/Reflection initialization.
3. **No safe read-only recovery path is currently evidenced.** Do not call either existing schema-initializing entry point from the snapshot CLI.
4. **Concrete storage design remains blocked.** Keep the logical Task Checkpoint authority and additive Task-layer direction, but do not choose a physical DB path, add a table, change `SCHEMA_VERSION`, or write runtime code.
5. **Next architecture decision needed:** explicitly choose whether the first product checkpoint store is (A) a new, independently configured Task/context store with its own documented lifecycle, or (B) a Task-layer extension of an existing application-provided connection once a real composition root is identified. The current source does not prove which deployment model exists, so this is a decision request, not an implementation instruction.

### SEQ 21 result

- [x] Recovery helper and caller-supplied path behavior inspected.
- [x] Diagnostic-only temporary database usage distinguished from production configuration.
- [x] Existing context repository's schema-mutating constructor confirmed.
- [x] Snapshot CLI confirmed not to load persisted task/checkpoint data.
- [ ] Canonical production composition root/configured DB path identified.
- [ ] Read-only, no-file-creation/no-DDL database access established.
- [ ] Concrete storage option explicitly accepted.

**Status:** source/configuration discovery reached a bounded UNKNOWN. Stop before runtime or schema edits until a concrete source or explicit architecture choice exists.
