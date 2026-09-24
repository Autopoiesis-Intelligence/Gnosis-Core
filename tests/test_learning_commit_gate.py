import pytest
from gnosis.self_learning.learning_commit_gate import commit_learning_outcome,is_committed,creates_execution_authority
def make(status="COMMITTED",verified=True,kind="LEARNING_SIGNAL"): return commit_learning_outcome(closure_verified=verified,closure_digest="sha256:closure",feedback_id="fb:1",learning_class=kind,evidence_refs=("e1",),status=status)
def test_verified_signal_can_commit(): assert is_committed(commit=make())
def test_unverified_closure_blocks():
 with pytest.raises(ValueError): make(verified=False)
def test_only_learning_classes_commit():
 with pytest.raises(ValueError): make(kind="REVIEW_REQUIRED")
def test_counterexample_can_commit(): assert is_committed(commit=make(kind="COUNTEREXAMPLE"))
def test_proposed_is_not_committed(): assert not is_committed(commit=make(status="PROPOSED"))
def test_evidence_required():
 with pytest.raises(ValueError): commit_learning_outcome(closure_verified=True,closure_digest="d",feedback_id="f",learning_class="LEARNING_SIGNAL",evidence_refs=())
def test_no_authority(): assert not creates_execution_authority(commit=make())
def test_deterministic(): assert make()==make()
