import pytest
from gnosis.self_learning.verification_feedback import record_verification_feedback,may_enter_learning,is_contract_bound,creates_execution_authority
def make(verdict="PASS"):
    return record_verification_feedback(contract_id="contract:1",contract_digest="sha256:c",execution_id="exec:1",scope="partner:a",expected_result="validated core",actual_result="validated core",evidence_refs=("e1",),verdict=verdict,deviation="none")
def test_feedback_is_recorded(): assert may_enter_learning(feedback=make())
def test_feedback_binds_contract(): assert is_contract_bound(feedback=make(),contract_id="contract:1",contract_digest="sha256:c",scope="partner:a")
def test_wrong_scope_breaks_binding(): assert not is_contract_bound(feedback=make(),contract_id="contract:1",contract_digest="sha256:c",scope="partner:b")
def test_evidence_required():
    with pytest.raises(ValueError): record_verification_feedback(contract_id="c",contract_digest="d",execution_id="e",scope="s",expected_result="x",actual_result="y",evidence_refs=(),verdict="FAIL",deviation="d")
def test_invalid_verdict():
    with pytest.raises(ValueError): make("UNKNOWN")
def test_no_authority(): assert not creates_execution_authority(feedback=make())
def test_deterministic(): assert make()==make()
