import pytest

from gnosis.self_learning.feedback_candidate_orchestration import (
    feedback_to_candidate,
)

COMMON = dict(
    result_id="result-1",
    evidence_refs=("ci:sha256:evidence",),
    rationale="verified observed result",
    facts=("alpha:beta", "gamma:delta"),
    normalization_id="norm-1",
    input_digest="sha256:input",
    objective="evaluate extracted relation",
    scope="first-task",
)

def test_verified_success_signal_reaches_shadow_candidate():
    candidate = feedback_to_candidate(outcome_class="SUCCESS_SIGNAL", **COMMON)
    assert candidate is not None
    assert candidate.status == "SHADOW"
    assert candidate.evidence_refs == ("ci:sha256:evidence",)
    assert candidate.pattern_refs
    assert candidate.relation_refs

def test_verified_counterexample_reaches_shadow_candidate():
    candidate = feedback_to_candidate(outcome_class="COUNTEREXAMPLE", **COMMON)
    assert candidate is not None
    assert candidate.status == "SHADOW"

@pytest.mark.parametrize("outcome_class", ["FAILURE", "INCONCLUSIVE"])
def test_non_learning_feedback_does_not_create_candidate(outcome_class):
    assert feedback_to_candidate(outcome_class=outcome_class, **COMMON) is None

def test_candidate_has_no_execution_authority():
    candidate = feedback_to_candidate(outcome_class="SUCCESS_SIGNAL", **COMMON)
    assert candidate is not None
    from gnosis.self_learning.feedback_candidate_orchestration import candidate_grants_execution_authority
    assert candidate_grants_execution_authority(candidate=candidate) is False
