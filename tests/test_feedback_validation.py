import pytest
from gnosis.self_learning.feedback_validation import create_feedback_validation,promotion_valid

def make(decision="PROMOTE"):
    return create_feedback_validation(proposal_id="sha256:proposal",privacy_check_refs=("privacy:pass",),generalization_check_refs=("generalization:pass",),scope_check_refs=("scope:pass",),exclusion_check_refs=("exclusion:pass",),validation_revision="r1",decision=decision)

def test_promotion_requires_all_validation_classes():
    assert promotion_valid(proposal_eligible=True,validation=make())

def test_proposal_failure_blocks_promotion():
    assert not promotion_valid(proposal_eligible=False,validation=make())

def test_hold_blocks_promotion():
    assert not promotion_valid(proposal_eligible=True,validation=make("HOLD"))

def test_reject_blocks_promotion():
    assert not promotion_valid(proposal_eligible=True,validation=make("REJECT"))

def test_identity_is_deterministic():
    assert make()==make()
