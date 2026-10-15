# Repository Role and Naming Contract

## Canonical names

- **Gnozis** is the public project/product brand.
- **Gnosis-Core** is the canonical repository for executable Core behavior, protected invariants, governed state transitions, and accepted implementation.
- **Genesis** is the protected factory and orchestration workspace. It may propose and coordinate work, but it is not an alternative name for Gnozis/Gnosis-Core and does not independently authorize Core mutations.
- **Gnosis-Memory** stores durable research context, provenance, and references. It is not execution authority.
- **Gnosis-Research** stores research and experiments. Research findings are inputs to engineering, not executable authority.
- **Gnosis** is the public registry/evidence/opportunity surface.
- **Gnosis-Knowledge** organizes reusable knowledge and sources.
- **Gnosis-Exchange** and **Gnosis-SDK** are planned integration surfaces; their README files describe intended scope, not a claim of a complete service or stable SDK.
- **Thoth** is a private scratch space for ideas, not canonical project state or authority.

## Direction of trust

Research / Knowledge / Memory / partner inputs
→ evidence and formalized requirements
→ implementation and verification in Gnosis-Core
→ explicit authorization and governance
→ accepted state transition / controlled release
→ publication of only approved, shareable results through Gnosis or other product surfaces.

Genesis may orchestrate factory work and call Core through explicit contracts. It must not bypass Core verification or act as an implicit authority source. Connectors, external models, research material, and generated candidates do not acquire execution authority by being present in the workflow.

## Authority and evidence rules

- A proposal, successful test, approval statement, or audit receipt is not by itself permission to mutate Core state.
- Authorization must be issued and verified through an independently trusted path and bound to the exact operation and evolution provenance.
- Persistence and an append-only audit chain provide durable/tamper-evident records; they do not establish that an authorization was truthful.
- Missing, incomplete, stale, revoked, or inconsistent authority must fail closed.
- No end-to-end production capability is claimed without current source, exact commit, relevant CI, and runtime evidence.

## Historical identifiers

Older names such as `Gnozis-V2` and `Mikhail-Kucheriavyi-23/Gnozis-V2` may appear in historical records, migration evidence, protocol identifiers, or source provenance. Preserve them when they identify historical artifacts or compatibility-sensitive interfaces. Do not use them as current canonical repository pointers. Any rename of code namespaces, schema IDs, or protocol identifiers requires a separate compatibility and migration review.

## Repository boundaries

- Public repositories may publish only information intended for public access.
- The private Genesis workspace is not a substitute for Core's authorization boundary.
- Research and memory repositories may inform decisions but cannot directly mutate protected Core state.
- Partner data, signing keys, private configuration, and other secrets must not be committed to public repositories or public artifacts.

## Status and change policy

This document defines repository roles and intended trust boundaries; it does not prove that a production composition root, issuer, key provisioning system, trusted-time source, revocation provider, or end-to-end runtime exists. Those capabilities require separate source-level and runtime evidence.

Update this contract when repository responsibilities actually change. Do not perform blind global replacements of historical names or protocol identifiers.
