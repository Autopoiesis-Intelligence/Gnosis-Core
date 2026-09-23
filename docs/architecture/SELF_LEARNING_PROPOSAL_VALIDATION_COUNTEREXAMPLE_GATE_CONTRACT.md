# E7.45 — Self-Learning Proposal Validation / Counterexample Gate

## Objective

Validate generated contract proposals before governance review by checking provenance, canonical identity, source finding presence, contract identity and supported finding classification.

## Boundary

The validation gate is adversarial evidence generation, not governance.

It MUST NOT:
- accept or activate proposals;
- mutate contracts;
- mutate Core state;
- grant permissions;
- copy private user/partner payloads.

## Required checks

At minimum:
1. proposal status is PROPOSED;
2. proposal identifier has SHA-256 form;
3. proposal can be deterministically reconstructed from its source finding;
4. proposal type is supported;
5. referenced contract is known when a contract set is supplied;
6. source finding is present when a finding set is supplied.

Failures MUST be explicit and machine-readable.

## Determinism

Equivalent proposal/input sets MUST produce equivalent ValidationResult sets and validation digest.

## Counterexample role

Validation MUST reject malformed, stale, unknown or identity-tampered proposals rather than silently repairing them.

## Status

IMPLEMENTED / UNVERIFIED.

Implementation:
- gnosis/self_learning/validation.py
- tests/test_self_learning_validation.py
