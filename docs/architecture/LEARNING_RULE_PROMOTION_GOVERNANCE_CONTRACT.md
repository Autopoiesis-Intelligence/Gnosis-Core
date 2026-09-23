# E7.17 — Learning Rule Promotion Governance Contract

## Objective

Define how verified learning results are classified before any rule or behavioral change can be proposed for canonical promotion.

## Promotion classes

Every VERIFIED learning result MUST receive one explicit class:

- OBSERVATION_ONLY — retained as knowledge; cannot create a rule.
- TEST_ONLY — may create or modify tests; cannot change production behavior.
- HYPOTHESIS — may generate candidates; requires further evaluation.
- SHADOW_RULE — may execute only in isolated shadow evaluation.
- PROMOTION_CANDIDATE — eligible for governance review.
- GOVERNANCE_REJECTED — retained as historical evidence but not promotable.
- EXPIRED — no longer valid under current revision/policy context.

## Separation of evidence and policy

Evidence verifies a claim. It does not itself define the policy under which that claim becomes executable behavior.

Therefore:

VerifiedEvidence != PromotionAuthorization

## Promotion requirements

A PROMOTION_CANDIDATE MUST have:

1. complete provenance;
2. valid source revisions;
3. resolved or explicitly classified evidence independence;
4. reproducible evaluation;
5. counterexample analysis;
6. compatibility result against current invariants;
7. defined rollback/supersession semantics;
8. governance decision;
9. immutable decision record.

## No automatic escalation

Repeated success, high frequency, agent consensus, partner reputation, or historical acceptance MUST NOT automatically escalate an item to PROMOTION_CANDIDATE.

## Regression protection

Before activation, the candidate MUST be checked against existing invariants and relevant regression tests.

A candidate that violates a protected invariant is rejected regardless of observed utility.

## Supersession

An accepted rule creates a new revision. Previous rules remain auditable and recoverable.

Rule supersession MUST NOT rewrite historical evidence.

## Acceptance

The contract is complete only when classification, promotion prerequisites, invariant regression protection, governance records and supersession are represented in code and tested.

Status: DESIGNED / NOT_IMPLEMENTED.
