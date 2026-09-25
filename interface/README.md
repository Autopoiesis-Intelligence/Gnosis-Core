# Gnozis Interface — Contract Execution Surface

This directory is the bootstrap specification for the future Gnozis-Interface repository.

## Boundary
Agent/client -> Interface -> Factory boundary -> Gnozis Core

The Interface executes declared contracts against an immutable Core revision and returns evidence-backed results.

## Result semantics
- PASS: all required assertions and evidence requirements satisfied.
- FAIL: an executed assertion violated the contract.
- BLOCKED: a required execution precondition was unavailable.
- NOT_IMPLEMENTED: a required capability does not exist.

The Interface does not mutate Core, edit contracts, silently change the target revision, or repair failures.

## First contract
CORE-MUTATION-BOUNDARY-01

The executable implementation remains a follow-up task; this bootstrap does not claim runtime verification.