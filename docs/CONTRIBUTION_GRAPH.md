# Gnozis Verifiable Contribution Graph

**Status:** ARCHITECTURAL BASELINE v0.1
**Date:** 2026-09-25

## Purpose

Represent a participant's verifiable history without reducing contribution quality to subjective ratings.

The graph records relationships between subjects, projects, contracts, artifacts, evidence and accepted results.

## Core graph

```
Subject
  -> Role
  -> Project
  -> Contract
  -> Deliverable
  -> Artifact
  -> Evidence
  -> Verification
  -> Acceptance
  -> Result
```

## Contribution record

A contribution record SHOULD contain:

- contribution_id;
- subject_id;
- organization context where applicable;
- project_id;
- role;
- contract_id where applicable;
- artifact references;
- evidence references;
- verification references;
- acceptance state;
- attribution;
- licensing/IP context;
- provenance.

## No reputation score

The base system does not assign a universal quality score, star rating or ranking.

It exposes verifiable facts from which a user or authorized party may make their own assessment.

## Attribution

Attribution should identify the contributor and contribution scope without implying ownership beyond the applicable contract or license.

## Negative records

Rejected, disputed or failed contributions may be recorded when relevant, with their provenance and resolution state.

A failed or disputed record must not be silently rewritten into success.

## Privacy

Contribution visibility may be:

- public;
- project participants;
- contracting parties;
- authorized reviewers;
- private.

Only the minimum information necessary should be exposed.

## Portability

A contribution record should be machine-readable and reference stable artifact identities so that a participant can demonstrate work across projects without transferring proprietary Kernel data.

## Trust boundary

Contribution history is evidence about completed interactions. It is not itself Kernel authority and cannot grant private access.

## Graph integrity

Important edges should reference immutable or revision-addressed artifacts and acceptance evidence.

Historical relationships should remain reconstructible after role changes or capability revocation.
