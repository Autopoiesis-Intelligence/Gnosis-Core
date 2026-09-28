import pytest

from gnosis.self_learning.e7_execution_observation import (
    ExecutionObservation,
    ExecutionObservationStatus,
)


@pytest.mark.parametrize(
    ("evidence", "expected", "causal"),
    [
        (
            ExecutionObservation("completed", "success", True, True, False),
            ExecutionObservationStatus.PASS,
            False,
        ),
        (
            ExecutionObservation("completed", "failure", True, True, True),
            ExecutionObservationStatus.FAIL_WITH_EVIDENCE,
            True,
        ),
        (
            ExecutionObservation("completed", "failure", False, False, False),
            ExecutionObservationStatus.UNOBSERVABLE_FAILURE,
            False,
        ),
        (
            ExecutionObservation("completed", "cancelled", False, False, False),
            ExecutionObservationStatus.CANCELLED,
            False,
        ),
    ],
)
def test_execution_classification(evidence, expected, causal):
    assert evidence.classification == expected
    assert evidence.permits_causal_attribution is causal


def test_failure_without_failure_output_cannot_be_causal():
    evidence = ExecutionObservation(
        "completed", "failure", True, True, False
    )
    assert evidence.classification == ExecutionObservationStatus.UNOBSERVABLE_FAILURE
    assert not evidence.permits_causal_attribution
