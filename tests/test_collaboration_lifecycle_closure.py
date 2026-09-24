import pytest
from gnosis.self_learning.collaboration_lifecycle_closure import create_lifecycle_closure,retirement_is_valid,closure_creates_authority
def make(state="VERIFIED_CLOSED",reason="VERIFIED_SUCCESS"):
    return create_lifecycle_closure(contract_id="E7.83",incident_id="incident:1",verification_id="verification:1",final_state=state,retirement_reason=reason,evidence_refs=("verification:1",),closed_at_evidence="closure:e1")
def test_verified_closure_is_retirable():
    assert retirement_is_valid(closure=make())
def test_blocked_closure_not_retirable():
    assert not retirement_is_valid(closure=make("BLOCKED","MANUAL_RETIREMENT"))
def test_manual_retirement_is_not_verified_closure():
    with pytest.raises(ValueError): make("VERIFIED_CLOSED","MANUAL_RETIREMENT")
def test_reopened_is_not_retired():
    assert not retirement_is_valid(closure=make("REOPENED","MANUAL_RETIREMENT"))
def test_closure_never_creates_authority():
    assert not closure_creates_authority(closure=make())
def test_identity_is_deterministic():
    assert make()==make()
