# Test Result Contract

**Version:** 0.1

Test results are machine-readable evidence objects, not commands to the Core.

Required identity and reproducibility fields:

- `candidate_id`
- `test_id`
- `test_policy_id`
- `test_policy_revision`
- `input_digest`
- `result`
- `evidence`
- `counterexamples`
- `deterministic`
- `result_sha256`

Allowed result values are `PASS`, `FAIL`, `INCONCLUSIVE` and `REJECTED`.

A `PASS` requires evidence. A `FAIL` requires at least one counterexample. Non-deterministic results are rejected by the contract.

The result contains no selection authority and no mutation/execution capability. It can be consumed by a later Select stage, but cannot select itself.
