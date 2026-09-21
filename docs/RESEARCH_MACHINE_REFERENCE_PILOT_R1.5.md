# R1.5 — Research → Engineering Reference Pilot

Status: PILOT CONTRACT
Purpose: demonstrate one real, provenance-preserving reference from Core-side engineering documentation to the canonical Gnozis Research Machine.

## Pilot source

Research Machine record: `C-0004`
Relation: `TEST_RATIONALE`

The referenced research proposition concerns the distinction between test validity and test adequacy. The pilot uses it only as rationale for verification design; it does not admit the claim into Core.

## Pilot target

Core-side contract: `docs/EVIDENCE_PROVENANCE_CONTRACT.md`

The contract independently requires that evidence verification scope be explicit and that an AI report not be treated as independent verification.

## Reference

```yaml
research_ref:
  repository: Mikhail-Kucheriavyi-23/Gnozis
  record_id: C-0004
  source_commit: 7eb7caeb6a82e09e3bf40feef515b4db25b3eb0c
  relation: TEST_RATIONALE
  note: Research rationale for distinguishing test validity from verification adequacy.
```

The source commit placeholder is intentional The exact introducing commit was resolved from the file path history. The commit message is `archive: atomize test validity versus test adequacy`. The reference is intentionally pinned to that historical commit.

## Pilot acceptance criteria

1. The reference identifies one stable Research Machine record.
2. The source commit is resolved from repository history.
3. The Core-side document does not copy the research claim as canonical truth.
4. The relation is explicit.
5. No runtime Core semantics change.
6. The reference remains historical/provenance traceable if C-0004 is later superseded.
7. A reviewer can navigate from the engineering contract to the source record and distinguish rationale from authority.

## Non-goals

- no runtime schema;
- no new database tables;
- no Research Machine import;
- no automatic synchronization;
- no Core mutation;
- no promotion of C-0004 to CORE-ADMITTED.

## Next action

Resolve the exact source commit for C-0004, then add the reference to the pilot contract.

## R1.5.1 provenance result

Resolved from the GitHub path history of `archive/records/C-0004.yaml`:

- introducing commit: `7eb7caeb6a82e09e3bf40feef515b4db25b3eb0c`
- commit message: `archive: atomize test validity versus test adequacy`
- parent: `e802af42621b4ff3c18a31836d4f9c2cfcab2fa4`

This is the exact commit used by the pilot reference. The current branch HEAD is not substituted for historical provenance.

### Pilot status

R1.5.1: COMPLETE.

The remaining R1.5 acceptance step is a navigation/reference audit: verify that a reviewer can resolve the Research Machine record from the pinned repository + record ID + source commit without requiring duplicated research content in V2.
