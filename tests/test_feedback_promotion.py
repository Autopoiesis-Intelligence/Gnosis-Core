import pytest
from gnosis.self_learning.feedback_promotion import create_promotion_record,promotion_record_valid

def make(decision="PROMOTED"):
    return create_promotion_record(validation_id="sha256:validation",proposal_id="sha256:proposal",source_delivery_receipt_id="sha256:delivery",target_knowledge_revision="knowledge:r2",promoted_finding_refs=("finding:1",),excluded_refs=("private:1",),decision=decision,record_revision="r1")

def test_promotion_record_requires_promote_validation():
    assert promotion_record_valid(validation_decision="PROMOTE",record=make())

def test_validation_hold_blocks_record_validity():
    assert not promotion_record_valid(validation_decision="HOLD",record=make())

def test_rejected_record_is_invalid():
    assert not promotion_record_valid(validation_decision="PROMOTE",record=make("REJECTED"))

def test_identity_is_deterministic():
    assert make()==make()
