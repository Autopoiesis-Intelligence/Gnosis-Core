# Repository Role and Naming Contract

Status: CURRENT ROLE CONTRACT — documentation only.

## Canonical repositories

| Repository | Role | Authority boundary |
|---|---|---|
| `Autopoiesis-Intelligence/Gnosis` | Public product and evidence surface | May publish selected, appropriate results and evidence; no direct Core or private factory authority. |
| `Autopoiesis-Intelligence/Gnosis-Core` | Canonical authority-bearing runtime and source of truth for accepted Core behavior | Sole canonical authority for protected state transitions, persistence, recovery, and admission of state changes. |
| `Autopoiesis-Intelligence/Gnosis-Genesis` | Protected module factory, orchestration, and commercial/private layer | May prepare candidates, evidence, and proposals and call explicit Core interfaces; is not a second canonical state authority. |
| `Autopoiesis-Intelligence/Gnosis-Memory` | Research, mathematics, provenance, and context material | Input/evidence only; no Core mutation authority. |
| `Autopoiesis-Intelligence/Gnosis-Research` | Research and diagnostic evidence workspace | No Core mutation authority; exact data contracts remain subject to their own accepted contracts. |
| `Autopoiesis-Intelligence/Gnosis-Knowledge` | Knowledge-related workspace | Detailed scope and consumers remain unresolved; no implicit Core mutation authority. |
| `Autopoiesis-Intelligence/Gnosis-Exchange` | Repository exists; detailed role not yet accepted | Unassigned; no authority inferred from its name. |
| `Autopoiesis-Intelligence/Gnosis-SDK` | Interface/SDK repository | Capability-scoped access only; no independent Core authority. |

This table records declared repository boundaries. It does not prove that every repository has a working implementation or an operational integration.

## Dependency and trust direction

```text
Gnosis-Memory / Gnosis-Research / Gnosis-Knowledge
                 │ evidence and proposals
                 ▼
Gnosis public product surface ── user-facing presentation
                 │
                 ▼
Gnosis-Genesis ── factory/orchestration; candidate generation
                 │ explicit Core contracts and requests
                 ▼
Gnosis-Core ── verification, governance gates, canonical state transition
```

The diagram expresses permitted architectural direction, not proof of a deployed end-to-end pipeline.

- `Gnosis-Core` must not import or require `Gnosis-Genesis`, research repositories, external AI, connectors, or commercial services.
- `Gnosis-Genesis` may propose modules, rules, evidence, or changes; proposals and successful tests do not grant execution authority.
- Only the protected Core authority path may admit canonical state changes.
- Public Gnosis may expose selected results/evidence but must not expose private factory internals or become an alternate authority root.
- Partner-private data and commercial configuration remain inside their explicitly authorized trust boundaries.

## Legacy naming

`Gnozis`, `Gnozis-V2`, and `Genesis/Genezis` are historical names, not current repository identities. Retain them only where needed to explain historical evidence or prior decisions; label such references as historical. Do not use them to redefine the current repository topology.

## Acceptance boundary

Repository-role documentation is not implementation evidence. Operational integration, runtime behavior, persistence, audit, and CI acceptance must be established independently against exact repository commits and evidence.

