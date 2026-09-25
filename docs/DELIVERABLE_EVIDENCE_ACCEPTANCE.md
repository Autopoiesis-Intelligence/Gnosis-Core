# Gnozis Deliverable, Evidence & Acceptance Chain

**Status:** ARCHITECTURAL BASELINE v0.1
**Date:** 2026-09-25

## Purpose

Define a verifiable chain from a contractual promise to a delivered result.

```
Requirement
  -> Deliverable
  -> Artifact
  -> Verification
  -> Acceptance
  -> Result
```

## Deliverable

A Deliverable is a bounded expected output defined by a Project or Contract.

Minimum semantics:

- deliverable_id;
- project_id;
- contract_id where applicable;
- description;
- acceptance criteria;
- expected artifact type;
- responsible party;
- due condition;
- status;
- provenance.

## Artifact

An Artifact is a concrete versioned output.

Examples:

- Git commit;
- repository revision;
- document;
- dataset;
- model;
- software build;
- research record;
- test result.

An artifact MUST be identifiable and reproducible to the extent required by its contract.

## Evidence

Evidence supports a claim about an artifact, process or result.

Evidence should identify:

- evidence_id;
- subject;
- source;
- revision or event;
- method;
- result;
- provenance;
- verification state.

Evidence does not automatically prove a claim. Its evidentiary status must remain explicit.

## Verification

Verification evaluates an artifact against defined criteria.

Verification methods may include:

- automated tests;
- reproducibility checks;
- schema validation;
- human review;
- independent review;
- experiment;
- benchmark;
- provenance validation.

The method must be appropriate to the acceptance criteria.

## Acceptance

Acceptance is a project/contract decision that the defined criteria have been satisfied.

Possible states:

- PENDING
- PASSED
- FAILED
- PARTIAL
- DISPUTED
- WAIVED

Acceptance MUST reference the criteria and relevant evidence.

## No silent acceptance

Repository activity alone does not imply acceptance.

A merged pull request, commit or uploaded file may be an artifact without being an accepted deliverable.

## Traceability

Where applicable:

```
Contract
  -> Requirement
  -> Deliverable
  -> Artifact
  -> Evidence
  -> Verification
  -> Acceptance
  -> Result
```

## Integrity

Important artifacts should retain:

- immutable revision;
- content digest;
- provenance;
- verification record.

Changing an artifact after verification creates a new artifact identity or revision and requires re-evaluation where applicable.

## Disputes

A disputed acceptance MUST preserve both the delivered artifact and the evidence used by each side.

The system should not rewrite historical acceptance decisions.

## Kernel boundary

Acceptance evidence can inform a Kernel process only through its normal evidence and authorization boundaries. Project acceptance cannot directly alter private Kernel state.
