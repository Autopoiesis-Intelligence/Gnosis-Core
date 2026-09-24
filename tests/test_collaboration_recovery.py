import pytest
from gnosis.self_learning.collaboration_recovery import create_recovery_record,recovery_preserves_original_evidence,recovery_allows_learning

def make(state="COMPENSATED",status="RECORDED"):
    return create_recovery_record(evidence_id="sha256:evidence",authorization_id="sha256:auth",attempt_id="attempt:1",original_result="FAILED",recovery_state=state,compensation_contract_id="E7.78-C",compensation_target="github:repo",reason="external mismatch",prior_evidence_digest="sha256:before",status=status,provenance_refs=("evidence:1","recovery:1"))

def test_compensated_recovery_is_learning_eligible():
    assert recovery_allows_learning(make())

def test_original_evidence_digest_is_immutable_reference():
    r=make()
    assert recovery_preserves_original_evidence(record=r,current_evidence_digest="sha256:before")
    assert not recovery_preserves_original_evidence(record=r,current_evidence_digest="sha256:after")

def test_manual_review_blocks_learning():
    assert not recovery_allows_learning(make("MANUAL_REVIEW"))

def test_failed_compensation_blocks_learning():
    assert not recovery_allows_learning(make("COMPENSATION_FAILED"))

def test_compensation_requires_contract():
    with pytest.raises(ValueError):
        create_recovery_record(evidence_id="e",authorization_id="a",attempt_id="t",original_result="FAILED",recovery_state="COMPENSATED",compensation_contract_id="",compensation_target="x",reason="r",prior_evidence_digest="d",status="RECORDED",provenance_refs=("p",))

def test_identity_is_deterministic():
    assert make()==make()
