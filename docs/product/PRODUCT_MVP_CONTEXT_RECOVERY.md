# Product MVP: Evidence-aware project context recovery

- Status: **IMPLEMENTATION SLICE — ACCEPTANCE PENDING**
- Canonical repository: `Autopoiesis-Intelligence/Gnosis-Core`
- Scope: local, read-only project handoff. No authorization or Core mutation.

## Invocation

From the repository checkout, with the package available in the Python environment:

```bash
python -m gnosis.context.cli --root .
```

The command prints schema-v1 JSON. Full source documents are excluded by default. For local debugging only, use:

```bash
python -m gnosis.context.cli --root . --include-source-documents
```

Unknown options are rejected by argparse with a usage error. The command is not a console-script entry point; use `python -m`.

## Fields and evidence semantics

The snapshot includes repository identity, branch, exact HEAD, active phase, active task, implementation, verification, acceptance, next permitted action, open findings, and missing sources. Material claims use a value and an explicit status, with source references where available.

- `OBSERVED`: read directly from local Git metadata or a canonical document.
- `REPORTED`: found in a document but not independently verified.
- `UNKNOWN`: no accepted source supports a value.
- `CONFLICT`: sources disagree; the snapshot does not silently select one.

A source file saying “PASS” is not by itself independent verification. The snapshot reports local evidence; it does not authorize state changes, external data transfer, or execution.

## Current limitations

Active task, implementation state, verification state, acceptance state, and open findings remain `UNKNOWN` unless a structured canonical source is available. This is intentional fail-closed behavior, but means the full handoff scenario is not yet accepted.

Repository identity can also be `CONFLICT` if the Git remote disagrees with repository labels in `AI_CONTEXT.md` or `STATUS.md`. Correct the canonical documents in a separate reviewed change rather than hiding the conflict.

## Acceptance checklist

- [x] Stable schema-v1 JSON shape and compact default output.
- [x] Raw source documents require an explicit opt-in flag.
- [x] Active phase is tied to `docs/PHASE_LEDGER.md#current-phase`.
- [x] Unknown values and repository identity conflicts are explicit.
- [x] Fixture and real-checkout CLI tests exist.
- [x] Focused CI tests pass on the initial isolated patch; see the PR for the latest exact run and baseline comparison.
- [ ] Full CI suite is green on the accepted commit.
- [ ] Empty checkout is verified not to create database/schema/files.
- [ ] Invalid CLI options have a documented and tested error contract.
- [ ] Output is reviewed against all six product questions and unresolved findings remain visible.
- [ ] Product owner/integration gate records acceptance.

## Evidence status

PR #170 currently remains Draft. The controlled docs-only baseline comparison found the same 35 failing/error test identifiers in the baseline and context-recovery merge CI; the six context-recovery tests passed. The overall repository suite remains failing, so this does not constitute full CI acceptance. Check live PR checks before relying on this status.
