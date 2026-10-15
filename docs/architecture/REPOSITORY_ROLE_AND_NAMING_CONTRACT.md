# Repository Role and Naming Contract

**Current identity (2026-10-15):** The canonical Core repository is `Autopoiesis-Intelligence/Gnosis-Core`. The Research Machine repository is `Autopoiesis-Intelligence/Gnosis`. Repository role and authority must be resolved from current repository state, not obsolete owner/repository names or historical project snapshots.

## Canonical repository

**Gnosis-Core** is the canonical Gnozis Core repository.

It is the source of truth for executable Core behavior, protected invariants, governed transitions and accepted implementation.

## Temporary self-learning archive

A separate second repository is reserved for the temporary self-learning archive.

Its role is NOT to be a second Core.

It stores and organizes:
- theoretical material;
- mathematical/formal derivations;
- evidence and counterexamples;
- research context;
- agent/partner contributions;
- provenance and learning lineage;
- machine-readable learning material;
- experimental/self-optimization knowledge.

Its contents are inputs to governed learning, not canonical executable authority.

## Direction of trust

Self-learning archive -> quarantine/workspace -> verification -> governance -> Gnosis-Core.

Never:

Self-learning archive -> direct Core mutation.

## Naming rule

Until the second repository receives an explicit final name, documentation MUST refer to it descriptively as:

**Temporary Self-Learning Archive**

or

**Self-Learning Research & Learning Archive**

and MUST NOT call it Core, canonical Core, production Core, or a second Gnozis Core.

The `Autopoiesis-Intelligence/Gnosis` repository is the verified Research Machine source. It is distinct from the canonical `Gnosis-Core`; references to a future Temporary Self-Learning Archive are historical until a current repository and accepted role are independently verified.

## Partner repositories

Partner repositories are external sources. They are not the Temporary Self-Learning Archive and are not Core.

PartnerRepository -> Temporary Self-Learning Archive -> governed learning -> Gnosis-Core.

Status: CONTRACT / NAMING BASELINE.
