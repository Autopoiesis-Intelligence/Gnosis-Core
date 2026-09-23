import pytest
from gnosis.self_learning.feedback_proposal import create_feedback_proposal,promotion_eligible

def make():
    return create_feedback_proposal(delivery_receipt_id="sha256:receipt",partner_id="partner-a",source_scope="partner:finance",artifact_refs=("artifact:1",),privacy_filters=("remove-private",),generalizable_findings=("finding:1",),exclusion_refs=("private-data:excluded",),revision="r1")

def test_feedback_requires_valid_delivery_and_privacy():
    assert promotion_eligible(receipt_valid=True,privacy_valid=True,proposal=make())

def test_invalid_delivery_blocks_promotion():
    assert not promotion_eligible(receipt_valid=False,privacy_valid=True,proposal=make())

def test_privacy_failure_blocks_promotion():
    assert not promotion_eligible(receipt_valid=True,privacy_valid=False,proposal=make())

def test_identity_is_deterministic():
    assert make()==make()
