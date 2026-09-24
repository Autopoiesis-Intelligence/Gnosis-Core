import pytest
from gnosis.self_learning.feedback_integration import admit_feedback,may_enter_learning,requires_review,creates_execution_authority
def make(verdict="PASS",kind="LEARNING_SIGNAL",status="ADMITTED"): return admit_feedback(feedback_id="fb:1",contract_id="c:1",scope="partner:a",verdict=verdict,evidence_refs=("e1",),learning_class=kind,status=status)
def test_pass_can_enter_learning(): assert may_enter_learning(admission=make())
def test_fail_can_be_counterexample(): assert may_enter_learning(admission=make("FAIL","COUNTEREXAMPLE"))
def test_fail_cannot_be_positive_signal():
    with pytest.raises(ValueError): make("FAIL","LEARNING_SIGNAL")
def test_inconclusive_requires_review(): assert requires_review(admission=make("INCONCLUSIVE","REVIEW_REQUIRED"))
def test_inconclusive_cannot_be_signal():
    with pytest.raises(ValueError): make("INCONCLUSIVE","LEARNING_SIGNAL")
def test_proposed_not_admitted(): assert not may_enter_learning(admission=make(status="PROPOSED"))
def test_no_authority(): assert not creates_execution_authority(admission=make())
def test_deterministic(): assert make()==make()
