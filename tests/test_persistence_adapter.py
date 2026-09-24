import pytest
from gnosis.self_learning.persistence_adapter import build_commit_plan,failure_requires_rollback,commit_proof_complete

def make(): return build_commit_plan(request_id="req:1",state_digest="sha256:s",candidate_id="cand:1",idempotency_key="idem:1")
def test_plan(): assert make().audit_event_type=="PARTNER_LEARNING_COMMIT"
def test_required_identity():
 with pytest.raises(ValueError): build_commit_plan(request_id="",state_digest="s",candidate_id="c",idempotency_key="i")
@pytest.mark.parametrize("p",["state_insert","candidate_insert","transition_insert","audit_insert","head_update","commit"])
def test_failure_rollback(p): assert failure_requires_rollback(failure_point=p)
def test_commit_proof(): assert commit_proof_complete(head_state_id="s2",transition_to_state_id="s2",transition_from_state_id="s1",previous_head="s1",candidate_parent_state_id="s1",audit_verified=True)
def test_bad_proof(): assert not commit_proof_complete(head_state_id="s1",transition_to_state_id="s2",transition_from_state_id="s1",previous_head="s1",candidate_parent_state_id="s1",audit_verified=True)
