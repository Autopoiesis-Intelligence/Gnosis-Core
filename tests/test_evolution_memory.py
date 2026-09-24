import pytest
from gnosis.self_learning.evolution_memory import admit_verified,may_enter_next_cycle,creates_execution_authority
def make(status="ADMITTED",outcome="VERIFIED",observed="sha256:new"):
    return admit_verified(verification_id="verify:1",commit_id="commit:1",verified_state_digest="sha256:new",evidence_refs=("memory:e1",),learning_scope="self_learning",status=status,verification_outcome=outcome,observed_state_digest=observed)
def test_verified_state_can_enter_memory(): assert may_enter_next_cycle(entry=make())
def test_unverified_cannot_enter_memory():
    with pytest.raises(ValueError): make(outcome="FAILED")
def test_mismatched_state_cannot_enter_memory():
    with pytest.raises(ValueError): make(observed="sha256:other")
def test_rejected_entry_cannot_feed_cycle(): assert not may_enter_next_cycle(entry=make("REJECTED"))
def test_memory_never_grants_authority(): assert not creates_execution_authority(entry=make())
def test_deterministic(): assert make()==make()
