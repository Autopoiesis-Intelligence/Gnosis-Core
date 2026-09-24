# External Audit Core Hardening Contract

## Purpose
Translate the September 2026 external audit into evidence-gated engineering tasks without treating auditor recommendations as established implementation facts.

## Findings accepted for verification
1. State/transition purity and side-effect isolation.
2. Guard completeness for canonical mutations.
3. Recursive/cascade failure containment.
4. Public Core typing quality.
5. Environment reproducibility.
6. Architecture Decision Records.
7. Explicit legal/licensing decision.

## Findings requiring qualification
- mypy --strict is a verification target, not an automatic requirement for every module.
- Poetry/uv is an implementation option; reproducible builds and dependency locking are the actual requirement.
- Aider/Codeium configuration is optional unless an explicit project policy requires it.
- GPLv3 is not assumed. License selection must follow the project's intended research/commercial policy and be recorded explicitly.
- Directory naming alone does not prove isolation; import/runtime dependency analysis is required.

## Acceptance
Each finding must end in IMPLEMENTED, PARTIAL, MISSING or NOT_APPLICABLE with concrete evidence. No audit recommendation may silently become a design requirement.

Status: ACTIVE / AUDIT-DERIVED.
