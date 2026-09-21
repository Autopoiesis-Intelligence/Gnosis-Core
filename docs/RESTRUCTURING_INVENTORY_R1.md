# Gnozis-V2 — Restructuring Inventory R1

Status: ACTIVE
Baseline: main @ 914162968da479fe40ec53fd4f0e8e7ff489fa01

## Objective

Separate the canonical engineering Core from research/history material without losing provenance or breaking the currently implemented architecture.

This is a structural engineering task, not a documentation cleanup.

## Classification

| Path | Classification | Decision |
|---|---|---|
| gnosis/core/ | CORE | KEEP |
| gnosis/evolution/ | CORE-ADJACENT RUNTIME | KEEP; contains governed transition/transaction machinery |
| gnosis/storage/ | CORE-ADJACENT RUNTIME | KEEP; canonical durable state/audit persistence |
| gnosis/instances/ | CORE-ADJACENT RUNTIME | KEEP; instance/clone/fork semantics require explicit audit before movement |
| gnosis/reflection/ | CORE-ADJACENT RESEARCH/RUNTIME | KEEP FOR NOW; active read-only reflection runtime; later boundary review |
| gnosis/context/ | INTERFACE / TRACK-A | KEEP FOR NOW; user/task continuity runtime is not Research Machine merely because it handles context |
| context/PROJECT_CONTEXT.json | OPERATIONAL HANDOFF | KEEP |
| tests/ | TEST / EVIDENCE | KEEP; tests are executable verification assets |
| .github/ | TOOLING / CI | KEEP |
| pyproject.toml | TOOLING | KEEP |
| docs/AI_CONTEXT.md, STATUS.md and current contracts | OPERATIONAL DOCUMENTATION | KEEP; not historical research by default |
| docs/architecture/ and current implementation contracts | ARCHITECTURE / CONTRACT | KEEP |
| logs/audit/ | EVIDENCE / HISTORICAL VERIFICATION | CANDIDATE FOR RESEARCH MACHINE; do not move until provenance/index contract is defined |
| logs/ci/ | CI EVIDENCE | KEEP or later export; current CI evidence must remain addressable |
| logs/README.md | ARCHITECTURE NOTE | KEEP until logging boundary is redesigned |
| diagnostic_corpus/ | RESEARCH / EXPERIMENTAL EVIDENCE | CANDIDATE FOR RESEARCH MACHINE; preserve exact source commit and scenario provenance |
| archive/ | SUPERSEDED TRANSITIONAL STRUCTURE | DO NOT EXPAND; reconcile/remove after Research Machine destination is established |
| README.md | PROJECT ENTRYPOINT | KEEP, update after boundary is physically established |
| AUDIT.md | CURRENT AUDIT / EVIDENCE INDEX | KEEP initially; later distinguish active audit from historical research |
| LICENSE-RESEARCH.md | RESEARCH POLICY | KEEP; verify scope during Research Machine separation |
| COMMERCIAL-LICENSE.md | PRODUCT / LEGAL | KEEP |
| TRADEMARKS.md | PRODUCT / LEGAL | KEEP |
| AGENT_ROLES.md | OPERATIONAL GOVERNANCE | KEEP |

## Initial conclusions

1. gnosis/core/ is already a clean semantic nucleus and must not be contaminated with research migration.
2. gnosis/reflection/ is not automatically Research Machine material: it is an active bounded runtime layer and must be evaluated by responsibility, not by name.
3. diagnostic_corpus/ is the clearest first Research Machine candidate because its own contract describes it as reproducible experimental evidence rather than canonical production history.
4. logs/audit/ is also a Research Machine candidate, but current audit evidence must remain traceable from the engineering baseline before movement.
5. context/PROJECT_CONTEXT.json and operational contracts are not historical research merely because they describe the project.
6. The temporary archive/ directory is not the target architecture and must not become a third state/memory system.

## Next bounded action

Perform a controlled extraction of diagnostic_corpus/ into the Gnozis Research Machine model, preserving:
- source commit;
- scenario identity;
- generation method;
- raw artifact;
- verification status;
- relationship to the Core baseline.

Only after that extraction is verified should logs/audit/ be considered for migration.

## Non-goals

- no Ψ-Core semantic rewrite;
- no reflection redesign;
- no mass documentation rewrite;
- no deletion of historical evidence;
- no automatic Core↔Research Machine synchronization yet.