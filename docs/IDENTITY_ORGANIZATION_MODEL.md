# Gnozis Identity & Organization Model

**Status:** ARCHITECTURAL BASELINE v0.1
**Date:** 2026-09-25

## Purpose

Define a neutral identity boundary for people and organizations interacting with Gnozis.

Identity is separate from Kernel authority. Knowing who a subject is does not grant access to proprietary state.

## Subject types

- PERSON
- ORGANIZATION
- PROJECT
- SERVICE

A person or organization may hold multiple roles.

## Roles

Supported ecosystem roles include:

- USER
- RESEARCHER
- CONTRACTOR
- PARTNER
- INVESTOR
- MAINTAINER

Role assignment is contextual and does not imply unrestricted authority.

## Organization membership

A person may act on behalf of an organization only within an explicitly recorded relationship.

The relationship may include:

- subject_id;
- organization_id;
- role;
- scope;
- status;
- start/end conditions;
- verification evidence.

## Identity states

```
DISCOVERED
  -> REGISTERED
  -> VERIFIED
  -> ACTIVE

              -> SUSPENDED
              -> REVOKED
```

Verification state is distinct from trust in the subject's research or commercial claims.

## Privacy principle

Only the minimum identity information required for a capability or contract should be exposed to another party.

Public knowledge contributions may use a public identity, pseudonym or organization attribution according to the applicable contribution and licensing rules.

## Capability authorization

Authorization is granted to a subject for a specific capability and scope.

```
Identity
  -> Role
  -> Capability
  -> Scope
  -> Policy
  -> Permission
```

Role alone MUST NOT grant Kernel access.

## Contract relationship

A contract may reference verified subjects and organizations.

The contract defines obligations and permitted actions; identity verification establishes the subject boundary.

## Kernel boundary

Identity services can establish who is requesting an action. They cannot directly mutate Kernel state.

All Kernel influence remains subject to the Kernel's own authorization, validation and evolution contracts.

## Audit

Security-relevant actions SHOULD retain:

- subject identifier;
- organization context where applicable;
- capability;
- scope;
- policy version;
- artifact;
- result;
- timestamp or event identifier;
- provenance.

Identity records should not be used as substitutes for evidence records.
