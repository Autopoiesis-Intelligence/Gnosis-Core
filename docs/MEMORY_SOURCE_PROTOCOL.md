# Gnozis Memory Source Protocol

**Status:** ARCHITECTURAL BASELINE v0.1
**Date:** 2026-09-25

## Purpose

The Memory Source Protocol defines how an external or domain repository becomes an authorized, versioned knowledge source for the private Gnozis Kernel.

A repository is never trusted solely because it belongs to the Gnozis organization.

## Protocol lifecycle

```
DISCOVER
  -> REGISTER
  -> AUTHENTICATE
  -> SYNC
  -> VALIDATE
  -> QUARANTINE / CANDIDATE
  -> EVALUATE
  -> VERIFY
  -> ACCEPT / REJECT
  -> INCORPORATE (optional)
```

## Source identity

Each source MUST have a stable source identifier and an explicit owner.

Minimum identity record:

- source_id
- owner_id
- repository_locator
- domain
- contract_version
- declared license
- current revision identifier

## Authorization

Authorization is capability-based and scoped to the source.

Supported conceptual permissions:

- READ
- ANNOTATE
- PROPOSE
- PUBLISH

The protocol does not grant DELETE or history-rewrite authority to the Kernel by default.

Permissions MUST be independently revocable.

## Revision integrity

Every synchronized revision MUST retain:

- source_id;
- repository revision / commit identifier;
- content digest;
- schema version;
- retrieval metadata;
- provenance metadata.

A mutable branch name is not sufficient evidence of identity.

## Validation

Before consumption, the source revision is checked for:

1. source authorization;
2. revision integrity;
3. schema conformance;
4. provenance completeness;
5. malformed or contradictory records;
6. forbidden authority claims;
7. dependency integrity;
8. policy/licensing constraints.

Failure MUST result in rejection or quarantine, not silent acceptance.

## Evidence semantics

The protocol MUST distinguish at least:

- established evidence;
- verified derivation;
- observation;
- model;
- hypothesis;
- conjecture;
- interpretation;
- unresolved question;
- counterexample;
- rejected claim.

Storage does not convert one class into another.

## Kernel influence boundary

A Memory Source can provide evidence and candidates.

It cannot directly mutate trusted Kernel state.

The only valid influence path is:

```
Memory Source
 -> candidate
 -> Kernel evaluation
 -> verified evidence
 -> authorized transition
 -> Kernel state
```

## Synchronization

Sources may be synchronized periodically or on explicit events.

Synchronization MUST be idempotent and revision-addressed.

A previously accepted revision must remain reproducible from its recorded identity and digest.

## Quarantine

A source or revision enters QUARANTINE when:

- identity cannot be verified;
- provenance is incomplete;
- schema validation fails;
- content integrity fails;
- policy is violated;
- duplicate/conflicting authority is detected;
- verification is inconclusive.

Quarantine MUST prevent the revision from silently influencing trusted state.

## Incorporation

Verification does not automatically require incorporation.

The Kernel may:

- accept as reference memory;
- accept as evidence;
- generate a candidate transition;
- defer;
- reject;
- quarantine.

Incorporation into trusted state requires the normal Kernel evolution contract and evidence chain.

## Audit requirements

Each meaningful protocol event SHOULD be attributable to:

- source;
- revision;
- content digest;
- operation;
- policy version;
- verification result;
- Kernel decision;
- resulting state/transition where applicable.

The protocol therefore preserves the distinction between persistence, retrieval, consumption and influence.

## Compatibility

The protocol is domain-neutral. Mathematics, physics, philosophy, engineering, biology and future domains use the same trust boundary.

Domain-specific schemas may extend the common protocol but may not weaken its provenance, authorization or verification requirements.
