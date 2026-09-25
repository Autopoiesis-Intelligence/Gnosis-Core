# CORE-MUTATION-BOUNDARY-01

## Purpose
Define the executable trust boundary for Core mutation. The contract must establish that external reflection/evolution machinery cannot mutate canonical Core state or source except through an explicitly governed transition path.

## Contract
A candidate proposal MUST NOT:
- mutate canonical Psi state directly;
- bypass verify();
- activate itself;
- modify Core source;
- alter persistence semantics silently;
- substitute execution input/state identity.

A permitted mutation MUST be represented by an explicit transition and remain attributable to the exact Core source SHA and input/state digests.

## Required evidence
1. Exact Core source SHA.
2. Exact execution input identity.
3. State identity and state digest.
4. Candidate/proposal identity.
5. Verification result.
6. Audit/provenance record.
7. Negative evidence for direct/bypass mutation attempts.
8. Durable evidence that rejected transitions do not become committed state.

## Closure rule
The contract is CLOSED only when the boundary is demonstrated by reproducible runtime tests and persisted audit evidence. Documentation alone is insufficient.

## Evidence closure
- Runtime adversarial boundary tests: PASS
- Durable rejected-transition evidence: PASS
- Bypass/fail-closed tests: PASS
- Canonical Core source-integrity manifest: PASS
- CI matrix: Python 3.11 + 3.12 PASS
- Verified CI run: #2694
- PR evidence record: PR #80

## Current status
CLOSED

## Closure basis
All required evidence items are satisfied by reproducible runtime tests, canonical source-integrity verification, durable persistence checks, and CI run #2694. PR #80 remains open as a governance record; its open state does not invalidate the technical contract closure.