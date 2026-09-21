# Research Machine Reference Contract — R1.4

Status: CONTRACT / ACTIVE
Scope: Gnozis-V2 references to the canonical Gnozis Research Machine
Authority: non-authoritative reference only

## Purpose

Provide the smallest stable mechanism for Gnozis-V2 to point to a Research Machine record without copying its semantics into Core or granting the research record authority.

## Minimal reference

A Core-side reference consists of:

```yaml
research_ref:
  repository: Mikhail-Kucheriavyi-23/Gnozis
  record_id: C-0004
  source_commit: <exact source commit>
  relation: DERIVED_REQUIREMENT
```

The same shape may be used for `R-*`, `E-*`, `X-*`, `D-*`, `A-*` and `T-*` records when the relation is appropriate.

## Required fields

- `repository`: canonical Research Machine repository identifier.
- `record_id`: stable Research Machine record ID.
- `source_commit`: exact commit from which the referenced record was read.
- `relation`: why the Core artifact references the record.

## Optional fields

- `record_version`: schema version when needed for disambiguation.
- `path`: repository-relative record path when useful for navigation.
- `note`: short engineering-context note; must not duplicate the research statement.

## Allowed relation values

Initial controlled vocabulary:

- `INFORMED_BY` — research informed engineering reasoning but does not itself define a requirement.
- `DERIVED_REQUIREMENT` — an explicit Core requirement was derived from the research item.
- `TEST_RATIONALE` — the research item explains why a verification case exists.
- `COUNTEREXAMPLE_SOURCE` — the research item supplies a challenge/counterexample basis.
- `AUDIT_REFERENCE` — an audit explicitly references the research item.

A relation is provenance metadata, not authority.

## Authority boundary

A `research_ref` MUST NOT:

- authorize a Core mutation;
- replace a Core invariant;
- replace verification evidence;
- imply that the referenced research item is true;
- imply that the referenced research item is accepted by Core;
- cause automatic activation.

The Core must independently validate applicability and complete its normal implementation, verification and acceptance path.

## Identity and immutability

Research Machine IDs are stable identifiers. A changed research record must be represented by its repository history/schema lifecycle rather than silently changing the meaning of an existing Core reference.

The `source_commit` makes the reference reproducible even if the research record is later superseded.

## Core-side placement

This contract is metadata only. It should be attached to an existing engineering artifact such as a task, requirement, contract, audit or test rationale.

Do not create a parallel ResearchRecord state model inside `gnosis/core/`.

## Example

```yaml
research_ref:
  repository: Mikhail-Kucheriavyi-23/Gnozis
  record_id: C-0184
  source_commit: 0717671589facc8ca51e3943c11a1a405f5e
  relation: TEST_RATIONALE
  note: Evidence-generation timing must be tested for temporal leakage.
```

The example is illustrative. It does not mean C-0184 is Core-admitted.

## Acceptance

R1.4 is complete when:

1. a Core engineering artifact can cite a Research Machine record with this minimal reference;
2. the reference is provenance-reproducible;
3. no research content is duplicated into Core;
4. no authority is transferred by the reference;
5. the reference can survive research-record supersession without losing historical traceability.

## Next

Use one existing engineering task/contract as a pilot reference. Do not modify runtime semantics solely to add the reference.
