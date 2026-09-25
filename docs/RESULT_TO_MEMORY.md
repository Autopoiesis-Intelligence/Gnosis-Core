# Gnozis Result → Memory Contribution

**Status:** ARCHITECTURAL BASELINE v0.1
**Date:** 2026-09-25

## Purpose

Define how completed work can become reusable knowledge without allowing project output to bypass Memory Source validation or the private Kernel trust boundary.

## Closed loop

```
Result
  -> Knowledge Contribution
  -> Memory Source
  -> Registry
  -> Validation
  -> Verification
  -> Eligible for Kernel consumption
```

## Result

A Result is the accepted outcome of a Project, Contract or research activity.

It may be:

- research finding;
- dataset;
- software/library;
- engineering design;
- validated method;
- benchmark;
- documentation;
- domain model;
- other reusable artifact.

## Knowledge Contribution

A Knowledge Contribution proposes that a Result become reusable knowledge.

It should reference:

- result_id;
- contribution_id;
- source project;
- artifact/revision;
- contributor(s);
- license/IP basis;
- provenance;
- target Memory Source;
- proposed record type;
- evidence;
- verification state.

A contribution is a proposal, not automatic publication.

## Memory Source admission

The target Memory Source evaluates the contribution according to its schema, governance and licensing rules.

```
PROPOSED
  -> VALIDATING
  -> ACCEPTED
  -> PUBLISHED
```

Exceptional states:

- REJECTED
- QUARANTINED
- WITHDRAWN

## Registry relationship

Only registered Memory Sources may participate in the standard ecosystem protocol.

A contribution cannot silently register a new source or expand source permissions.

## Kernel consumption

Publication into a Memory Source does not automatically authorize Kernel influence.

Kernel consumption requires:

1. authorized Memory Source;
2. pinned revision;
3. valid provenance;
4. schema validation;
5. applicable verification;
6. Kernel-side evidence evaluation.

## Attribution and IP

Contribution records must preserve applicable attribution and license/IP terms.

A contribution cannot change ownership merely by being copied into a Memory Source.

## Revisions

A corrected or changed knowledge record creates a new revision and must preserve its relationship to the previous revision.

Where a change affects evidence or conclusions, re-validation may be required.

## Rejection

Rejected contributions remain auditable where policy permits. Rejection does not become silent deletion.

## Security principle

No external Result can directly mutate private Kernel state.

The only permitted path is:

```
Result
 -> Contribution
 -> Memory Source
 -> Registry
 -> Validation / Verification
 -> Kernel evidence boundary
```
