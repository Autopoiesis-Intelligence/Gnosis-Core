# Gnozis Project & Workspace Model

**Status:** ARCHITECTURAL BASELINE v0.1
**Date:** 2026-09-25

## Purpose

A Project is the bounded unit in which an opportunity becomes coordinated work.

A Workspace is the controlled working context for a Project. It connects people, contracts, capabilities, repositories and deliverables without exposing the private Kernel by default.

## Project

Minimum semantic fields:

- project_id;
- title;
- objective;
- opportunity_id;
- participants;
- roles;
- contracts;
- capabilities;
- repositories;
- tasks;
- deliverables;
- acceptance criteria;
- evidence;
- status;
- provenance.

## Workspace

A Workspace provides scoped access to the resources required for the Project.

It may contain references to:

- public repositories;
- private project repositories;
- datasets;
- research records;
- tasks;
- contract artifacts;
- validation results;
- communication records.

A Workspace is not the Kernel and does not automatically expose Kernel state.

## Lifecycle

```
DISCOVERED
  -> PROPOSED
  -> APPROVED
  -> ACTIVE
  -> VALIDATING
  -> COMPLETED
  -> ARCHIVED
```

Exceptional states:

- PAUSED
- CANCELLED
- DISPUTED

## Resource relationship

```
Opportunity
    |
    v
Project
    |
    +--> Contracts
    +--> Participants
    +--> Capabilities
    +--> Repositories
    +--> Tasks
    +--> Deliverables
    +--> Evidence
    |
    v
Result
```

## Repository relationship

A Project may reference multiple repositories.

Examples:

- research repository;
- domain Memory Source;
- software repository;
- data repository;
- documentation repository.

Repository membership does not itself define contractual authority.

## Participant access

Workspace access is derived from:

- identity;
- organization relationship;
- role;
- capability;
- project scope;
- contract;
- policy.

Least privilege is the default.

## Deliverables

A deliverable must be independently identifiable and may reference:

- repository;
- revision;
- artifact digest;
- dataset version;
- research record;
- test or validation result.

Acceptance is determined by the relevant contract criteria.

## Completion

A completed Project should retain enough provenance to reconstruct:

```
Opportunity
 -> Project
 -> Participants
 -> Contracts
 -> Work
 -> Artifacts
 -> Evidence
 -> Acceptance
 -> Result
```

The Workspace may then be archived while durable public or contractual records remain available according to their policies.

## Kernel boundary

Project execution can consume approved capabilities and approved Memory Sources.

Project state cannot directly mutate private Kernel state. Any Kernel influence must pass through the Kernel's authorization, evidence and evolution contracts.
