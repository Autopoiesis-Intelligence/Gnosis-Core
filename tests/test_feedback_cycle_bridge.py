import pytest

from gnosis.self_learning.feedback_cycle_bridge import (
    learning_influence_is_bound,
    start_cycle_from_feedback,
)
from gnosis.self_learning.feedback_integration import admit_feedback


def make_admission(**overrides):
    values = {
        "feedback_id": "feedback:1",
        "contract_id": "contract:e806",
        "scope": "sandbox",
        "verdict": "FAIL",
        "evidence_refs": ("evidence:failure",),
        "learning_class": "COUNTEREXAMPLE",
        "status": "ADMITTED",
    }
    values.update(overrides)
    return admit_feedback(**values)


def test_rejected_feedback_can_become_a_bound_counterexample_cycle():
    admission = make_admission()
    link, cycle = start_cycle_from_feedback(
        admission=admission,
        parent_cycle_id="cycle:0",
        parent_state_digest="sha256:state0",
        input_refs=admission.evidence_refs,
        scope="sandbox",
    )
    assert learning_influence_is_bound(
        link=link, admission=admission, cycle=cycle
    )
    assert cycle.parent_memory_entry_id == admission.admission_id


def test_non_admitted_feedback_cannot_influence_next_cycle():
    admission = make_admission(status="PROPOSED")
    with pytest.raises(ValueError):
        start_cycle_from_feedback(
            admission=admission,
            parent_cycle_id="cycle:0",
            parent_state_digest="sha256:state0",
            input_refs=admission.evidence_refs,
            scope="sandbox",
        )


def test_positive_learning_requires_non_failure_signal():
    with pytest.raises(ValueError):
        make_admission(verdict="FAIL", learning_class="LEARNING_SIGNAL")
