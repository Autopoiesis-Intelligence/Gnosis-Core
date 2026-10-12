# Product MVP: Evidence-aware project context recovery

- Status: **MVP DEFINITION — implementation scope not yet accepted**
- Date: 2026-10-12
- Repository: `Autopoiesis-Intelligence/Gnosis-Core`
- Related architecture: [ADR-001](../architecture/ADR-001-CORE-PRODUCT-BOUNDARY.md), [Context continuity contract](../CONTEXT_CONTRACT.md)

## Product problem

Project work currently depends too heavily on reconstructing the active task from long AI conversations. The product should let a connected AI terminal recover a compact, durable and evidence-aware handoff from repository state without treating chat history as canonical.

## First user-visible scenario

A user opens a project checkout and runs one read-only command. The command returns a compact handoff answering:

1. Which repository, branch and exact HEAD are being inspected?
2. Which task/phase is active, and which canonical file states that?
3. What is implemented, what is verified, and what remains only reported or unknown?
4. Which unresolved blockers matter to the next action?
5. What is the next permitted action and what evidence supports it?
6. Which fields are unknown or stale rather than silently inferred?

The command must work without network access, without initializing Core's database/schema, and without modifying the checkout.

## Current implementation found

- `gnosis/context/cli.py` exposes a read-only command that prints JSON.
- `gnosis/context/snapshot.py` reads `docs/PHASE_LEDGER.md`, `AI_CONTEXT.md`, and `STATUS.md`, and reports repository URL, branch, and HEAD using Git.
- The snapshot currently includes the entire contents of those three documents under `source_documents`.
- It currently sets `active_task`, `implementation_state`, `verification_state`, and `acceptance_state` to generic `UNKNOWN` strings and returns an empty `open_findings` list.
- Therefore, this is a useful read-only primitive, but it is **not yet a compact task recovery product**. Its current output can be large and does not derive the active task or blockers from structured canonical records.
- Source inspection is not runtime proof. Exact-head CI was not yet checked for the later documentation-only ADR commit when this MVP was defined.

## MVP boundary

### Include

- Keep the interface read-only and local-first.
- Return repository identity and exact HEAD.
- Return a compact handoff, not entire source documents by default.
- Provide explicit source references for each material status claim.
- Distinguish `OBSERVED`, `REPORTED`, `VERIFIED`, `UNKNOWN`, and `CONFLICT` (or an equally explicit, documented vocabulary).
- If canonical task/phase data cannot be safely resolved, return `UNKNOWN` plus the missing source; do not infer a task from a convenient phrase.
- Offer an explicit opt-in flag to include raw source documents for debugging, if retaining that behavior is useful.
- Preserve the no-database-initialization guarantee.

### Exclude

- Authentication, identity, cryptographic authorization, secrets, encryption or external connectors.
- Writing/updating task state.
- Core state mutation, candidate execution, authorization issuance or commits.
- Automatic trust-context provisioning.
- Treating AI output, an issue title, or a chat message as canonical state without an explicit durable source contract.
- Claiming independent verification just because a source file says PASS.

## Acceptance criteria

1. **CLI contract:** documented invocation and stable JSON schema; invalid options fail with a useful error.
2. **Read-only:** running the command does not create or alter Core/context databases, files, or Git state.
3. **Identity:** output includes the exact repository identifier, branch (or an explicit detached/unknown state), and HEAD SHA when Git metadata is available.
4. **Bounded output:** default output excludes full `AI_CONTEXT.md` and `STATUS.md` bodies; source references and selected evidence excerpts are bounded.
5. **Evidence binding:** every active-task, verification, acceptance, or blocker claim points to a canonical file/section or is explicitly marked unknown.
6. **Conflict behavior:** stale repository identifiers or conflicting handoff sources produce `CONFLICT`/unknown with both source references; no silent selection.
7. **No authority escalation:** snapshot fields and connected-tool availability never imply authorization to mutate Core or send data externally.
8. **Recovery tests:** test a normal checkout, missing Git metadata, missing source documents, stale/conflicting source values, and empty checkout; no schema initialization in an empty database location.
9. **Exact CI:** record the resulting commit SHA and CI run, including Python versions and full result. CI proves only tested behavior.
10. **Runtime evidence:** run the documented command against a clean fixture and a real repository checkout; capture exit code and schema-valid output.
11. **Acceptance review:** compare output to the six user questions above; unresolved findings stay visible.

## Implementation sequence

1. Inspect current CLI/snapshot tests and define the output schema before changing code.
2. Add focused tests for bounded output, explicit unknowns, repository identity and no side effects.
3. Implement the smallest compatible change to `gnosis/context/snapshot.py` and `gnosis/context/cli.py`.
4. Run focused tests, then full CI on the exact head.
5. Execute the command against a temporary fixture and a real checkout; preserve output as test/runtime evidence without committing private repository contents.
6. Update `STATUS.md` only from exact evidence; do not copy status claims from stale `context/PROJECT_CONTEXT.json`.

## Why this MVP first

It delivers immediate user value—recovering the real state of work across AI sessions—without needing an unproven production execution service, new credentials, a paid hosting layer, or changes to the canonical Core state machine. It is a product-facing slice, not a claim that cross-product context continuity is already implemented.

## Current status

- Product problem and first scenario: **DEFINED**.
- Existing read-only CLI/snapshot: **SOURCE PRESENT**.
- Compact evidence-aware task recovery: **NOT IMPLEMENTED / NOT ACCEPTED**.
- Runtime behavior on exact current head: **NOT PROVEN BY THIS DOCUMENT**.
- Next permitted action: inspect the actual tests for the CLI/snapshot and write the output contract tests before changing runtime behavior.
