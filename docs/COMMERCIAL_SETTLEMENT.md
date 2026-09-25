# Gnozis Commercial Settlement, IP & Licensing

**Status:** ARCHITECTURAL BASELINE v0.1
**Date:** 2026-09-25

## Purpose

Connect contractual work to commercial settlement while keeping payment execution, legal agreements and proprietary Kernel state separate.

## Commercial chain

```
Opportunity
  -> Proposal
  -> Contract
  -> Deliverable
  -> Verification
  -> Acceptance
  -> Settlement
  -> License / IP rights
```

## Settlement

A settlement record describes the financial consequence of an accepted contractual obligation.

It may reference:

- contract_id;
- deliverable_id;
- acceptance record;
- amount;
- currency;
- payer;
- payee;
- payment milestones;
- settlement status;
- external payment reference;
- dispute status;
- provenance.

Gnozis may coordinate settlement state but should not assume custody of funds unless a separately authorized financial system is used.

## Settlement states

```
PENDING
 -> DUE
 -> AUTHORIZED
 -> PROCESSING
 -> SETTLED

Exceptional:
DISPUTED
FAILED
CANCELLED
REFUNDED
```

## Milestones

Contracts may define multiple commercial milestones.

Each milestone should reference an explicit acceptance condition.

```
Milestone
  -> Deliverable
  -> Verification
  -> Acceptance
  -> Settlement
```

## Intellectual property

IP ownership is determined by the applicable contract and law, not by repository presence.

A contract may define:

- background IP;
- newly created IP;
- ownership;
- assignment;
- license grant;
- license scope;
- territory;
- duration;
- sublicensing;
- attribution;
- confidentiality.

## Licensing

Open-source and research artifacts should identify their license separately from contractual commercial terms.

A repository license does not automatically grant rights over unrelated proprietary Kernel technology.

## Commercial confidentiality

Public discovery may expose high-level commercial opportunity information.

Sensitive information such as negotiated rates, private financial data, confidential source material or proprietary Kernel details must remain within controlled access boundaries.

## Disputes

A settlement dispute must preserve:

- original contract;
- acceptance criteria;
- deliverable;
- evidence;
- verification result;
- settlement state;
- relevant communications or decisions where legally appropriate.

Historical records should not be silently rewritten.

## Security boundary

Payment credentials and financial account secrets MUST NOT be stored in ordinary Gnozis repositories.

External payment providers or controlled financial systems should be referenced by stable transaction identifiers where appropriate.

## Kernel boundary

Commercial settlement does not grant Kernel authority.

Financial completion may be evidence of contract completion, but cannot by itself authorize a Kernel state transition.
