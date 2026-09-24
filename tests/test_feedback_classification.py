import pytest
from gnosis.self_learning.feedback_classification import classify_partner_feedback,may_form_learning_candidate,may_enter_durable_learning
def make(kind="SUCCESS_SIGNAL",status="VERIFIED"): return classify_partner_feedback(result_id="r:1",outcome_class=kind,evidence_refs=("e1",),rationale="verified partner outcome",status=status)
def test_success_candidate(): assert may_form_learning_candidate(classification=make())
def test_counterexample_candidate(): assert may_form_learning_candidate(classification=make("COUNTEREXAMPLE"))
def test_failure_diagnostic_only(): assert not may_form_learning_candidate(classification=make("FAILURE"))
def test_inconclusive_hold(): assert not may_form_learning_candidate(classification=make("INCONCLUSIVE"))
def test_not_durable_commit(): assert not may_enter_durable_learning(classification=make())
def test_evidence_required():
 with pytest.raises(ValueError): classify_partner_feedback(result_id="r",outcome_class="SUCCESS_SIGNAL",evidence_refs=(),rationale="r")
def test_invalid_class():
 with pytest.raises(ValueError): classify_partner_feedback(result_id="r",outcome_class="UNKNOWN",evidence_refs=("e",),rationale="r")
def test_deterministic(): assert make()==make()
