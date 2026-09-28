"""Deterministic E7 runtime-observation fixture.

This is a local semantic execution harness. Its output is test evidence only;
it is not an exact-commit CI proof and does not mutate project state.
"""
from __future__ import annotations

from gnosis.self_learning.e7_execution_observation import (
    ExecutionObservation,
    ExecutionObservationStatus,
)


CASES = (
    (
        "success",
        ExecutionObservation("completed", "success", True, True),
        ExecutionObservationStatus.PASS,
        False,
    ),
    (
        "failure_with_evidence",
        ExecutionObservation("completed", "failure", True, True, True),
        ExecutionObservationStatus.FAIL_WITH_EVIDENCE,
        True,
    ),
    (
        "unobservable_failure",
        ExecutionObservation("completed", "failure", False, False),
        ExecutionObservationStatus.UNOBSERVABLE_FAILURE,
        False,
    ),
    (
        "cancelled",
        ExecutionObservation("completed", "cancelled", False, False),
        ExecutionObservationStatus.CANCELLED,
        False,
    ),
)


def main() -> int:
    for case_id, observation, expected, expected_causal in CASES:
        actual = observation.classification
        if actual != expected:
            print(f"FAIL {case_id}: expected={expected.value} actual={actual.value}")
            return 1
        if observation.permits_causal_attribution != expected_causal:
            print(
                f"FAIL {case_id}: expected_causal={expected_causal} "
                f"actual={observation.permits_causal_attribution}"
            )
            return 1
        print(
            f"PASS {case_id}: status={actual.value} "
            f"causal={observation.permits_causal_attribution}"
        )
    print("E7_EXECUTION_OBSERVATION_FIXTURE=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
