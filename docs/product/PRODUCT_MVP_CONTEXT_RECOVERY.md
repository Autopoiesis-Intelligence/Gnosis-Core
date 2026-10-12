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
- [x] Empty checkout returned UNKNOWN without creating files in CI run #3626 (Python 3.11 job).
- [x] Invalid CLI options return exit code 2 with argparse usage text in CI run #3626 (Python 3.11 job).
- [ ] Output is reviewed against all six product questions and unresolved findings remain visible.
- [ ] Product owner/integration gate records acceptance.

## Evidence status

PR #170 currently remains Draft. Latest observed head: `133486a74033e38f4171cb68e164ad1e1a35f26e`; merge-test SHA: `1aa7f92f1531b3489261cac2c210b225a44b8d46`. CI run #3626 failed overall (Python 3.11: 33 failed, 939 passed, 2 errors; Python 3.12 cancelled by fail-fast), but all eight context-recovery tests passed. CodeQL run #2505 and Import Graph run #1889 passed. A controlled docs-only baseline run #3624 on the same main base has the identical 35 failed/error test identifiers (33 failed + 2 errors), so this patch introduced no additional failures in that comparison. Dependency Review remains blocked because Dependency Graph is not enabled for the repository. Full suite green and product-owner acceptance remain pending. Check live PR checks before relying on this status.
