# Gnozis Memory Network Architecture

**Status:** ARCHITECTURAL BASELINE
**Date:** 2026-09-25

## Principle

Gnozis uses a **Private Kernel + authorized Memory Network + Capability Network** architecture.

The Kernel is the proprietary trust root. External repositories are not trusted merely because they are owned by or associated with Gnozis. They become usable memory sources only through explicit contracts, provenance and verification.

## Planes

### 1. Private Kernel

Repository target: `Gnozis-Kernel`

Owns proprietary state, relations, evolution, verification, governance, protected diagnostics and commercial intellectual property.

The Kernel never grants repository contents authority by default.

### 2. Memory Network

Domain repositories may hold independently versioned knowledge:

- mathematics;
- philosophy;
- physics;
- biology;
- engineering;
- computer science;
- economics;
- systems research;
- other future domains.

A memory repository is a **versioned knowledge substrate**, not Kernel state.

### 3. Capability Network

Genesis and authorized task repositories expose bounded capabilities to users and partners without exposing Kernel internals.

## Memory Source Contract

Every connected memory source MUST have an explicit machine-readable contract defining:

- source identity;
- owner;
- domain;
- read/write/propose permissions;
- synchronization mode;
- provenance requirements;
- schema version;
- verification policy;
- revocation state.

## Trust flow

```
Repository revision
  -> identity/provenance check
  -> digest and schema validation
  -> candidate
  -> Kernel evaluation
  -> verified evidence
  -> optional incorporation
```

A Git commit is never equivalent to trusted knowledge.

## Access levels

Memory sources may expose:

1. READ — Kernel may retrieve versioned material.
2. ANNOTATE — Kernel may attach machine-readable observations.
3. PROPOSE — Kernel may submit candidate changes or research requests.
4. PUBLISH — explicitly authorized automation may publish approved artifacts.

DELETE and history rewriting are not granted to Kernel by default.

## Local memory cache

The Kernel may maintain a local verified cache/index containing:

- repository identifier;
- commit SHA;
- content digest;
- schema version;
- verification status;
- provenance;
- synchronization metadata.

The cache is not an independent authority.

## Research feedback loop

```
Kernel observation
  -> research question
  -> external/domain repository
  -> new revision
  -> provenance + validation
  -> Kernel evaluation
  -> accepted/rejected/quarantined
```

This permits community and domain repositories to evolve independently while allowing the Kernel to periodically consume verified updates.

## Security invariant

**No repository is trusted merely because it belongs to the Gnozis ecosystem.**

Trust is established by identity + contract + provenance + validation + verification.

## Repository evolution

Do not create one giant Evidence repository when a domain has an independent lifecycle or community.

Create a dedicated repository when it has a meaningful boundary of:

- domain;
- ownership;
- lifecycle;
- access policy;
- provenance;
- community;
- licensing.

The Memory Network is therefore extensible rather than fixed to a predetermined number of repositories.
