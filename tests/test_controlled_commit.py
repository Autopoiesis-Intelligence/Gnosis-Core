from gnosis.self_learning.controlled_commit import create_controlled_commit,may_commit,is_fail_closed,grants_authority
def make(status="PROPOSED",base="sha256:base",result="sha256:new"):
    return create_controlled_commit(proposal_id="proposal:1",governance_decision_id="decision:1",base_state_digest=base,resulting_state_digest=result,transition_digest="sha256:t",evidence_refs=("commit:e1",),status=status)
def test_approved_matching_state_can_commit(): assert may_commit(commit=make(),governance_outcome="APPROVED",current_state_digest="sha256:base",required_result_digest="sha256:new")
def test_state_mismatch_fails_closed(): assert is_fail_closed(commit=make(),governance_outcome="APPROVED",current_state_digest="sha256:other",required_result_digest="sha256:new")
def test_nonapproved_fails_closed(): assert is_fail_closed(commit=make(),governance_outcome="REJECTED",current_state_digest="sha256:base",required_result_digest="sha256:new")
def test_same_state_is_not_commit(): assert not may_commit(commit=make(result="sha256:base"),governance_outcome="APPROVED",current_state_digest="sha256:base",required_result_digest="sha256:base")
def test_rejected_status_cannot_commit(): assert not may_commit(commit=make("REJECTED"),governance_outcome="APPROVED",current_state_digest="sha256:base",required_result_digest="sha256:new")
def test_commit_does_not_grant_authority(): assert not grants_authority(commit=make())
def test_deterministic(): assert make()==make()
