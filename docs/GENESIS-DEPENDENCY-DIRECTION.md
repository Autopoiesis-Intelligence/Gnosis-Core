# Genesis Dependency Direction

## Canonical direction

Trusted Core
  ↓
Genesis Runtime
  ↓
Product / Knowledge / Research / Commercial adapters

External layers may depend on Core contracts. Core must not depend on Genesis, Product, Knowledge, Research, Commercial, UI, connectors, or external model implementations.

## Rules

1. `gnozis_core` is the lowest trusted runtime boundary.
2. Genesis may call Core through explicit interfaces.
3. Genesis may propose state changes, modules, rules, or evidence, but Core verification decides whether trusted state can change.
4. Product services may orchestrate Genesis and Knowledge but cannot bypass Core verification.
5. Knowledge and Research are data/evidence sources, not execution authority.
6. Commercial services may consume proposals/evidence but cannot gain implicit access to private Genesis or user project data.
7. Connectors are adapters at the boundary and never become trusted Core dependencies.
8. External AI/model calls are orchestration dependencies, never hidden Core dependencies.
9. Persistence and audit implementations used by Core must remain deterministic and explicit.
10. Dependency direction is checked structurally and by tests before migration.

## Allowed examples

- Genesis → Core
- Product → Core
- Product → Genesis interfaces
- Product → Knowledge interfaces
- Commercial → Product interfaces
- Research → Knowledge/evidence interfaces

## Forbidden examples

- Core → Genesis
- Core → Research-Memory
- Core → LLM/API/connector
- Core → Commercial
- Knowledge → direct mutation of Core state
- Commercial → private Genesis internals
- Connector → direct database mutation of Core state

## Migration consequence

When a Genesis module violates this direction, first extract a small interface/contract at the lower boundary. Do not solve the violation by copying Genesis implementation into Core.
