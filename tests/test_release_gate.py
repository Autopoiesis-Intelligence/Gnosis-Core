import pytest
from gnosis.self_learning.release_gate import create_release_gate,release_eligible

def make(decision="RELEASE"):
    return create_release_gate(build_record_id="sha256:build",receipt_id="sha256:receipt",required_contracts=("E7.62","E7.67"),validation_refs=("ci:pass",),security_refs=("boundary:pass",),scope_refs=("scope:pass",),release_revision="r1",decision=decision)

def test_release_requires_all_evidence():
    assert release_eligible(receipt_status="PASSED",build_status="BUILT",gate=make())

def test_hold_blocks_release():
    assert not release_eligible(receipt_status="PASSED",build_status="BUILT",gate=make("HOLD"))

def test_unpassed_receipt_blocks_release():
    assert not release_eligible(receipt_status="PARTIAL",build_status="BUILT",gate=make())

def test_identity_is_deterministic():
    assert make()==make()

def test_invalid_decision_is_rejected():
    with pytest.raises(ValueError): make("UNKNOWN")
