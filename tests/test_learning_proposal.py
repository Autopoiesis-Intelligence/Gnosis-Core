from gnosis.self_learning.learning_proposal import create_proposal,may_propose,proposal_grants_execution_authority,proposal_is_bound_to_state
from gnosis.self_learning.shadow_evaluation import evaluate_candidate

def make(status="PROPOSED",base="sha256:base"):
    return create_proposal(candidate_id="cand:1",evaluation_id="eval:1",base_state_digest=base,objective="improve routing",scope="core:self_learning",evidence_refs=("e1",),status=status)

def shadow(candidate_id="cand:1", outcome="PASS", evidence=("e1",)):
    return evaluate_candidate(candidate_id=candidate_id,base_state_digest="sha256:base",projected_state_digest="sha256:new",invariant_results=("PASS:invariant",),regression_results=("PASS:regression",),evidence_refs=evidence,outcome=outcome)

def proposal_for(s):
    return create_proposal(candidate_id=s.candidate_id,evaluation_id=s.evaluation_id,base_state_digest=s.base_state_digest,objective="improve routing",scope="core:self_learning",evidence_refs=s.evidence_refs)

def test_pass_shadow_allows_proposal():
    s=shadow(); assert may_propose(proposal=proposal_for(s),shadow_evaluation=s)

def test_fail_shadow_blocks_proposal():
    s=shadow(outcome="FAIL"); assert not may_propose(proposal=proposal_for(s),shadow_evaluation=s)

def test_non_proposed_cannot_propose():
    s=shadow(); p=proposal_for(s); p=create_proposal(candidate_id=p.candidate_id,evaluation_id=p.evaluation_id,base_state_digest=p.base_state_digest,objective=p.objective,scope=p.scope,evidence_refs=p.evidence_refs,status="BLOCKED"); assert not may_propose(proposal=p,shadow_evaluation=s)

def test_state_binding():
    assert proposal_is_bound_to_state(proposal=make(),current_state_digest="sha256:base") and not proposal_is_bound_to_state(proposal=make(),current_state_digest="sha256:other")

def test_proposal_never_grants_authority():
    assert not proposal_grants_execution_authority(proposal=make())

def test_foreign_evaluation_cannot_propose():
    s=shadow(); assert not may_propose(proposal=make(),shadow_evaluation=s)

def test_foreign_evidence_cannot_propose():
    s=shadow(); p=create_proposal(candidate_id=s.candidate_id,evaluation_id=s.evaluation_id,base_state_digest=s.base_state_digest,objective="improve routing",scope="core:self_learning",evidence_refs=("foreign",)); assert not may_propose(proposal=p,shadow_evaluation=s)

def test_foreign_candidate_cannot_propose():
    s=shadow(candidate_id="cand:other"); p=create_proposal(candidate_id="cand:1",evaluation_id=s.evaluation_id,base_state_digest=s.base_state_digest,objective="improve routing",scope="core:self_learning",evidence_refs=s.evidence_refs); assert not may_propose(proposal=p,shadow_evaluation=s)

def test_missing_shadow_artifact_cannot_propose():
    assert not may_propose(proposal=make(),shadow_evaluation=None)

def test_deterministic():
    assert make()==make()
