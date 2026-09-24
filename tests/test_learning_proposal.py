from gnosis.self_learning.learning_proposal import create_proposal,may_propose,proposal_grants_execution_authority,proposal_is_bound_to_state
def make(status="PROPOSED",base="sha256:base"):
    return create_proposal(candidate_id="cand:1",evaluation_id="eval:1",base_state_digest=base,objective="improve routing",scope="core:self_learning",evidence_refs=("e1",),status=status)
def test_pass_shadow_allows_proposal(): assert may_propose(proposal=make(),shadow_outcome="PASS")
def test_fail_shadow_blocks_proposal(): assert not may_propose(proposal=make(),shadow_outcome="FAIL")
def test_non_proposed_cannot_propose(): assert not may_propose(proposal=make("BLOCKED"),shadow_outcome="PASS")
def test_state_binding(): assert proposal_is_bound_to_state(proposal=make(),current_state_digest="sha256:base") and not proposal_is_bound_to_state(proposal=make(),current_state_digest="sha256:other")
def test_proposal_never_grants_authority(): assert not proposal_grants_execution_authority(proposal=make())
def test_deterministic(): assert make()==make()
