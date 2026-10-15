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
- [x] Empty checkout returned UNKNOWN without creating files in CI run #3628 (Python 3.11 and 3.12 jobs).
- [x] Invalid CLI options return exit code 2 with argparse usage text in CI run #3628 (Python 3.11 and 3.12 jobs).
- [ ] Output is reviewed against all six product questions and unresolved findings remain visible.
- [ ] Product owner/integration gate records acceptance.

## Evidence status

PR #170 remains Draft. Exact latest observed head before this documentation refresh: `e5499d7768b3f32eea80d94e4158482bf074356a`; CI run #3628 failed overall on both Python 3.11 and 3.12 (each: 33 failed, 939 passed, 18 warnings, 2 errors). All eight context-recovery tests passed on both jobs. CodeQL run #2509 and Import Graph run #1898 passed. Controlled docs-only baseline run #3624 on the same main base has the same 35 failure/error identifiers (33 failed + 2 errors); no additional failure/error was introduced in that comparison. Dependency Review run #1050 is blocked/fails because Dependency Graph is not enabled/available for the repository; this is not a vulnerability finding. Full suite green, review of all six product questions, runtime continuity, and product-owner acceptance remain pending. This paragraph is a record of the preceding tested head; any new commit must be checked separately before relying on exact-head CI status.
