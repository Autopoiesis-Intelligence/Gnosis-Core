# GNV2-003 — adversarial bypass finding

Status: HISTORICAL FINDING — corrective implementation present; fresh runtime/CI evidence pending

## Finding

`gnosis/core/invariants.py` correctly defines `check_meaningful_change()` and includes it in `DEFAULT_INVARIANTS`.

However, Current `gnosis/core/verification.py::evaluate()` executes protected invariants before the custom Test function. A custom Test is evaluated only after protected invariants pass, and its return value is subject to the strict bool contract.

`gnosis/core/evolution.py::Engine.step()` commits only from the resulting `TestResult`.

The historical bypass described below is therefore no longer the current code path.

## Consequence

The architectural requirement is implemented in source and covered by the new adversarial regression `tests/test_protected_invariants_custom_test.py`.

It must not yet be marked CI VERIFIED because no fresh workflow result for the current HEAD is available.

## Required evidence

Run the targeted regression and full CI suite on the current HEAD. The test must demonstrate that a content-identical candidate with only a version increment and `custom TestFn=lambda current, candidate: True` is rejected and that Engine.state remains unchanged. A genuine content change must still be accepted when protected invariants and the custom Test both pass.
