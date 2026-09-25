# Gnozis Execution Plan

Date: 2026-09-25
Status: ACTIVE
Purpose: ordered execution plan derived from the current repository/contract audit.

## Gate 0 — Topology and contract control
- Keep Gnozis as public evidence/opportunity surface.
- Keep Gnozis-Research-Memory as machine-readable research/mathematics/provenance/context.
- Keep Genesis/Genezis as protected Core + Module Factory.
- Treat Mnemosyne, Hermes, Thoth, Athena, Hephaestus, Prometheus and Daedalus as contract-first specialized repositories.
- Do not grant any specialized repository Core mutation authority.

Status: 90% complete.

## Gate 1 — P0 persistence/recovery acceptance
Active blockers:
- Issue #16: P0-R2 persistence/recovery correctness.
- Reconcile the fixture correction before accepting any failure result.
- Prove semantic transition tamper fails closed.
- Prove duplicate provenance/audit links produce controlled recovery failure.
- Prove transition replay/idempotency behavior.
- Keep recovery authorization explicit.
- Require exact Python 3.11/3.12 CI evidence.
- Do not alter Core semantics, protected commit path, governance authority, audit meaning, fail-closed boundary, or provenance identity model.

Status: 55% acceptance — BLOCKED pending exact current-main evidence.

Latest verified historical candidate evidence: PR #33 records green CI on exact head `596f6f85f5909f22f68d059b00a6c1dccf9f0a3f` for Python 3.11/3.12 and CodeQL, but explicitly states that main was not yet verified after consolidation. Dependency Review remained unavailable/unverified. Therefore this evidence is historical candidate evidence, not current-main acceptance.

## Gate 2 — E7 consolidation
Open verification branches/PRs must be treated as evidence candidates, not independently accepted contracts.
Consolidate E7.49–E7.77 into the Contract Registry with exact SHA and evidence references.
Resolve duplicate/shadowed definitions before accepting identity contracts.

Status: 70% — CONSOLIDATION REQUIRED. PRs #39–#54 and later E7 work remain evidence candidates until their guarantees are reconciled against the accepted current main.

## Gate 3 — Mutation and integration boundaries
- PR #80: CORE-MUTATION-BOUNDARY-01.
- PR #81: CORE-INTEGRATION-BOUNDARY-01.
Acceptance requires independent adversarial verification on the reconciled main, not branch-only evidence.

Status: 60% — PENDING Gate 1.

## Gate 4 — Reflection and cycle evidence
- PR #79: R3.1 CycleEvidence.
- PR #77: E7.15 deterministic vertical slice.
- Verify evidence lineage, replay determinism, rejected/inconclusive commit prohibition, and persistence integration.
- These remain evidence infrastructure and do not grant autonomous mutation authority.

Status: 60% — PENDING Gates 1–3.

## Gate 5 — Governance
Define and verify:
- proposal vs authority;
- authorization;
- activation;
- monitoring;
- rollback;
- explicit human/external boundary;
- atomic transition/audit/evidence binding.

Status: 30% — NOT ACCEPTED.

## Gate 6 — Research-Memory
Create the dedicated machine-readable memory repository structure.
Migrate:
- AI_CONTEXT;
- mathematical corpus;
- evidence/provenance;
- epochs/history;
- research branches;
- contract references.
Separate accepted contracts from historical hypotheses and research notes.

Status: 5% — PLANNED.

## Gate 7 — Specialized repositories
Before implementation, each repository must receive:
REPOSITORY-ID, PURPOSE, INPUTS, OUTPUTS, OWNED DATA, DEPENDENCIES, AUTHORITY, TRUST BOUNDARY, PROVENANCE, FAILURE MODES, ACCEPTANCE TESTS, NON-GOALS.

Order:
Mnemosyne → Hermes → Thoth → Athena → Hephaestus → Prometheus → Daedalus.

Status: 0% implementation; contract preparation follows Gate 6.

## Gate 8 — Controlled autonomous evolution
Only after all preceding gates have accepted evidence:
observe → diagnose → candidate → counterexample → shadow → verify → govern → authorize → commit → observe outcome → learn.

No stage may inherit mutation authority silently.

Status: future / gated.

## Current rule
No broad new Core architecture and no autonomous mutation while Gate 1 is unresolved. Verification, bounded fixes, contract consolidation, documentation and evidence generation are allowed.


## Gate 1 verification checklist — current repository configuration

Checked 2026-09-25:
- CI matrix explicitly runs Python 3.11 and 3.12.
- CI installs the package with dev dependencies and runs pytest with coverage.
- CodeQL runs for Python and GitHub Actions on main/PR/schedule.
- Dependency Review workflow exists for pull requests and fails on high severity.
- These workflow definitions establish intended checks but do not themselves prove that the latest canonical main has successful runs.
- Current acceptance therefore still requires successful workflow-run evidence attached to the accepted main SHA. The connector reports no commit status records and no pull-request-triggered workflow runs for the current documentation commits checked here. The available GitHub connector does not expose a workflow-dispatch operation, so this cannot be resolved by triggering Actions from this execution surface. This is an evidence gap, not a pass. The repository-side workflow configuration remains valid.
