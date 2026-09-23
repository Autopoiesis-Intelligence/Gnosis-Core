import pytest
from gnosis.self_learning.execution_receipt import create_execution_receipt,delivery_eligible

def make(status="PASSED"):
    return create_execution_receipt(plan_id="sha256:plan",input_revision="data:r1",executed_revision="exec:r1",result_refs=("result:1",),test_evidence=("ci:pass",),invariant_evidence=("psi:pass",),boundary_evidence=("scope:pass",),status=status,created_revision="r1")

def test_passed_receipt_is_delivery_eligible():
    assert delivery_eligible(make())

def test_failed_receipt_is_not_delivery_eligible():
    assert not delivery_eligible(make("FAILED"))

def test_receipt_identity_is_deterministic():
    assert make()==make()

def test_invalid_status_is_rejected():
    with pytest.raises(ValueError): make("UNKNOWN")
