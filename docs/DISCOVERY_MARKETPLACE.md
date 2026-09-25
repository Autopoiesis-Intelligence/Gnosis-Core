# Gnozis Discovery & Opportunity Marketplace

**Status:** ARCHITECTURAL BASELINE v0.1
**Date:** 2026-09-25

## Purpose

Provide a human-facing discovery layer for knowledge, research, capabilities, projects, contractors, partnerships and commercial opportunities.

The marketplace is a discovery and coordination layer. It does not expose private Kernel state.

## Discovery objects

A user may discover:

- Knowledge Domain
- Research Question
- Open Problem
- Opportunity
- Project
- Capability
- Contract opportunity
- Collaboration request
- Product / prototype
- Dataset or library
- Partnership opportunity
- Investment opportunity

## Search dimensions

Discovery should support:

- domain;
- topic;
- problem;
- capability;
- project stage;
- evidence state;
- required role;
- geography where intentionally relevant;
- licensing;
- commercial model;
- budget/resource range where public;
- availability;
- provenance;
- update/revision.

## Matching

The system may suggest relationships between a person or organization and an opportunity based on declared capabilities and explicit requirements.

A suggestion is not a guarantee of suitability, quality or outcome.

Final engagement remains a human decision and contract process.

## Opportunity lifecycle

```
DRAFT
 -> PUBLISHED
 -> DISCOVERABLE
 -> PROPOSALS
 -> SELECTED
 -> CONTRACTED
 -> EXECUTING
 -> COMPLETED
 -> ARCHIVED
```

Exceptional states:

- PAUSED
- WITHDRAWN
- DISPUTED
- CLOSED

## Marketplace surfaces

### Research

Questions, open problems, datasets, experiments and calls for contribution.

### Capabilities

Reusable software, engineering, analysis, research and other bounded capabilities.

### Projects

Active projects seeking participants, resources or services.

### Partnerships

Integration, distribution, research and commercial collaboration.

### Investment

Documented opportunities with appropriate commercial and evidence metadata.

## Evidence

Discovery cards should expose enough evidence metadata to help a user understand an opportunity without revealing confidential information.

Where applicable:

- evidence status;
- source references;
- verification state;
- revision;
- provenance;
- contribution history.

## No universal ranking

The base marketplace should not impose a universal score or ranking over people, research or opportunities.

Search and filtering should make relevant facts discoverable without converting them into an unexplained winner/loser ordering.

## Public/private boundary

Public discovery records may contain:

- description;
- scope;
- status;
- required capabilities;
- public evidence;
- licensing;
- public commercial terms.

Private details remain behind the appropriate identity, capability, contract and confidentiality boundaries.

## Conversion to work

```
Discovery
  -> Interest
  -> Proposal
  -> Project
  -> Contract
  -> Workspace
  -> Deliverable
  -> Acceptance
```

The marketplace therefore connects the open Gnozis surface to the controlled execution layer without granting direct Kernel access.
