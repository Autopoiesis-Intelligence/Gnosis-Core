import pytest

from gnosis.self_learning.e7_execution_evidence import (
    ExecutionEvidence,
    ExecutionStatus,
)


@pytest.mark.parametrize(
    ("evidence", "expected", "causal"),
    [
        (
            ExecutionEvidence("completed", "success", True, True, False),
            ExecutionStatus.PASS,
            False,
        ),
        (
            ExecutionEvidence("completed", "failure", True, True, True),
            ExecutionStatus.FAIL_WITH_EVIDENCE,
            True,
        ),
        (
            ExecutionEvidence("completed", "failure", False, False, False),
            ExecutionStatus.UNOBSERVABLE_FAILURE,
            False,
        ),
        (
            ExecutionEvidence("completed", "cancelled", False, False, False),
            ExecutionStatus.CANCELLED,
            False,
        ),
    ],
)
def test_execution_classification(evidence, expected, causal):
    assert evidence.classification == expected
    assert evidence.permits_causal_attribution is causal


def test_failure_without_failure_output_cannot_be_causal():
    evidence = ExecutionEvidence(
        "completed", "failure", True, True, False
    )
    assert evidence.classification == ExecutionStatus.UNOBSERVABLE_FAILURE
    assert not evidence.permits_causal_attribution
