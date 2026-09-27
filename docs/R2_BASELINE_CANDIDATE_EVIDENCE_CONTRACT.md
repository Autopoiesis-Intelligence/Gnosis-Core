# R2 Baseline / Candidate Execution Evidence Contract

Status: ACTIVE R2 CONTRACT — NOT VERIFIED
Contract ID: R2-CONTRACT-15
Scope: verification evidence for baseline/candidate comparison

## Purpose

A candidate execution must not be interpreted as a regression, improvement, or acceptance result unless a comparable baseline execution is available.

## Required execution identity

Every baseline or candidate verification record MUST identify:

- commit SHA
- repository/ref
- workflow definition revision
- execution/run identity
- job identity when available
- runtime/environment identity
- exact verification command
- result: PASS / FAIL / CANCELLED / UNKNOWN
- durable evidence reference, when available
- evidence digest when evidence is materialized into the Core evidence model

## Comparison rule

The implication `candidate_result -> regression` is prohibited unless a valid baseline execution record exists and the comparison dimensions are compatible.

Compatibility MUST include, at minimum:

- same verification contract revision
- same relevant verification command
- compatible runtime/environment
- identified repository revision for each side

## Evidence classes

These are distinct:

1. execution metadata
2. textual diagnostics
3. machine-readable test results
4. durable artifact references
5. Core-ingested evidence records

Presence of one class does not imply presence of another.

## Failure handling

If execution occurs but diagnostic evidence is unavailable:

- result remains OBSERVED-FAILURE
- root cause remains UNKNOWN
- no regression claim is allowed
- no acceptance decision may rely on the missing evidence

If baseline evidence is absent:

- candidate may be executed
- candidate result may be recorded
- candidate MUST NOT be compared causally against baseline
- promotion/acceptance remains blocked where baseline comparison is required

## Current R2 finding

For the current Genesis verification cycle:

- main baseline execution evidence is not presently available through the connected GitHub evidence surface
- PR #86 changed only CI evidence infrastructure
- PR #86 failure therefore does not establish an E7.108 defect
- E7.109 remains blocked until E7.108 and its evidence chain are independently accepted

## Acceptance conditions

R2-CONTRACT-15 becomes VERIFIED only when:

1. a canonical baseline execution record exists;
2. a canonical candidate execution record exists;
3. both reference retrievable evidence;
4. compatibility fields are checked;
5. comparison/causal attribution is tested;
6. missing-evidence and mismatched-baseline cases have negative tests;
7. the resulting evidence is linked to the applicable execution identity.

## Non-authority

GitHub Actions, artifacts, logs, or external CI providers are execution/evidence surfaces. They are not Core authority sources.

The Core evidence model MUST preserve enough provenance to distinguish external execution claims from Core-accepted evidence.
