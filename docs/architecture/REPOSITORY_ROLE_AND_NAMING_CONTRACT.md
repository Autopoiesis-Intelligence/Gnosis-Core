# Repository Role and Naming Contract

## Canonical repository

**Gnozis-V2** is the canonical Gnozis Core repository.

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

Self-learning archive -> quarantine/workspace -> verification -> governance -> Gnozis-V2 Core.

Never:

Self-learning archive -> direct Core mutation.

## Naming rule

Until the second repository receives an explicit final name, documentation MUST refer to it descriptively as:

**Temporary Self-Learning Archive**

or

**Self-Learning Research & Learning Archive**

and MUST NOT call it Core, canonical Core, production Core, or a second Gnozis Core.

The historical `Gnozis` repository remains the legacy/research/archive line and is distinct from both the canonical `Gnozis-V2` Core and the future Temporary Self-Learning Archive.

## Partner repositories

Partner repositories are external sources. They are not the Temporary Self-Learning Archive and are not Core.

PartnerRepository -> Temporary Self-Learning Archive -> governed learning -> Gnozis-V2 Core.

Status: CONTRACT / NAMING BASELINE.
