# Gnozis Ecosystem Roles & Contract Network

**Status:** ARCHITECTURAL BASELINE v0.1
**Date:** 2026-09-25

## Purpose

The Gnozis ecosystem must support people and organizations around the private Kernel without exposing Kernel internals.

The ecosystem separates knowledge, opportunities, contracts, execution and proprietary intelligence.

## Primary roles

### Researcher

Creates, investigates or validates research questions and evidence.

Typical flow:

```
Research Question -> Research Task -> Contribution -> Verification -> Attribution
```

### Contractor

Executes a bounded technical or operational capability under an explicit contract.

Typical flow:

```
Opportunity -> Requirements -> Proposal -> Contract -> Execution -> Acceptance
```

### Investor

Evaluates documented opportunities, evidence, commercial models and resource requirements.

The investor surface exposes commercial evidence and opportunity metadata, not proprietary Kernel internals.

### Partner

Collaborates through a defined capability, research, distribution, integration or commercial agreement.

### Maintainer

Maintains an open repository, schema, library or research resource according to its governance and provenance rules.

### User

Consumes a capability, product or result without receiving internal authority over the system.

## Role separation

A person or organization may hold multiple roles, but each action is evaluated against the role and contract scope under which it is performed.

## Opportunity

An Opportunity is a structured record describing a problem, capability, research direction, product possibility or commercial need.

Minimum fields:

- opportunity_id;
- title;
- type;
- problem;
- desired outcome;
- scope;
- evidence;
- status;
- required capabilities;
- dependencies;
- estimated resources;
- IP/licensing requirements;
- contact/engagement channel;
- provenance.

## Contract

A Contract is an explicit agreement connecting parties to a bounded outcome.

Minimum semantic fields:

- contract_id;
- parties;
- roles;
- scope;
- deliverables;
- acceptance criteria;
- timeline;
- compensation;
- IP ownership;
- licensing;
- confidentiality;
- security requirements;
- termination conditions;
- referenced repositories/artifacts;
- provenance;
- status.

A repository or Git commit may be a referenced deliverable or evidence artifact, but it is not itself a contract.

## Contract lifecycle

```
DISCOVER
  -> PROPOSE
  -> NEGOTIATE
  -> ACCEPT
  -> EXECUTE
  -> VERIFY
  -> ACCEPTED / DISPUTED / TERMINATED
```

The system must preserve the distinction between a proposal and an accepted agreement.

## Capability boundary

Contracts grant bounded rights to perform a defined capability.

A contractor, researcher, partner or user does not receive general Kernel access merely by entering a contract.

## Evidence and acceptance

Deliverables can reference versioned artifacts, commits, datasets, research records or test results.

Acceptance should be tied to explicit criteria rather than informal repository presence.

## Commercial separation

Public opportunity records may describe:

- problem;
- market/application;
- desired capability;
- evidence;
- status;
- resources sought.

Confidential commercial terms and proprietary Kernel information remain in controlled systems.

## Traceability

Where appropriate, the ecosystem should be able to trace:

```
Person / Organization
 -> Role
 -> Opportunity
 -> Contract
 -> Artifact
 -> Evidence
 -> Acceptance
 -> Result
```

This provides a common structure for research, contracting, partnership and commercial workflows without turning the public repositories into a private CRM or legal system.
