import pytest
from gnosis.self_learning.remediation_verification import create_verification,closure_is_valid
def make(result="VERIFIED",closure="CLOSED",scope="public:proposal",observed="public:proposal"):
    return create_verification(authorization_id="auth:1",plan_id="plan:1",incident_id="incident:1",action="COMPENSATE",target_resource="github:repo",authorized_scope=scope,observed_scope=observed,result_status=result,target_before="sha256:before",target_after="sha256:after",evidence_refs=("evidence:after",),verification_basis="independent verification",closure_state=closure)
def test_verified_matching_result_closes():
    assert closure_is_valid(verification=make())
def test_non_verified_cannot_close():
    with pytest.raises(ValueError): make("FAILED","CLOSED")
def test_verified_requires_closed_state():
    with pytest.raises(ValueError): make("VERIFIED","MANUAL_REVIEW")
def test_scope_mismatch_is_not_valid_closure():
    assert not closure_is_valid(verification=make("MISMATCH","REOPEN_REQUIRED","public:proposal","private:other"))
def test_unknown_does_not_close():
    assert not closure_is_valid(verification=make("UNKNOWN","MANUAL_REVIEW"))
def test_identity_is_deterministic():
    assert make()==make()
