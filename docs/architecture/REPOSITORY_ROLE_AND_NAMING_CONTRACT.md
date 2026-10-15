# Repository Role and Naming Contract

**Current identity (2026-10-15):** The canonical Core repository is `Autopoiesis-Intelligence/Gnosis-Core`. The Research Machine repository is `Autopoiesis-Intelligence/Gnosis`. Repository role and authority must be resolved from current repository state, not obsolete owner/repository names or historical project snapshots.

## Canonical repository

**Gnosis-Core** is the canonical Gnozis Core repository.

It is the source of truth for executable Core behavior, protected invariants, governed transitions and accepted implementation.

## Historical archive concept (not an active repository assignment)

Older project plans described a separate temporary self-learning archive. That plan is historical context, not proof that a second repository currently exists or has been assigned this role.

No repository may be treated as the archive until its live identity, visibility, ownership, contents, and accepted role are checked against current GitHub state and explicitly recorded. Archive contents, if any, are inputs to governed learning and are not canonical executable authority.

## Direction of trust

If a separate archive is explicitly approved in a future phase: archive -> quarantine/workspace -> verification -> governance -> Gnosis-Core.

Never:

Self-learning archive -> direct Core mutation.

## Naming rule

If a future archive repository is explicitly approved, documentation should refer to it descriptively until its final name is approved:

**Temporary Self-Learning Archive**

or

**Self-Learning Research & Learning Archive**

and must not call it Core, canonical Core, production Core, or a second Core.

The `Autopoiesis-Intelligence/Gnosis` repository is the verified Research Machine source. It is distinct from the canonical `Gnosis-Core`; references to a future Temporary Self-Learning Archive are historical until a current repository and accepted role are independently verified.

## Partner repositories

Partner repositories are external sources. They are not the Temporary Self-Learning Archive and are not Core.

Future flow, only if a separate archive is explicitly approved: PartnerRepository -> approved archive -> governed learning -> Gnosis-Core.

Status: CONTRACT / NAMING BASELINE.
