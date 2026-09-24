from gnosis.self_learning.governance_decision import decide,may_commit,is_stale,creates_execution_authority
def make(outcome="APPROVED",approvals=2,base="sha256:base",current="sha256:base"):
    return decide(proposal_id="proposal:1",proposal_base_state_digest=base,current_state_digest=current,evidence_refs=("gov:e1",),required_approvals=2,approvals=approvals,outcome=outcome)
def test_approved_matching_state_can_commit(): assert may_commit(decision=make())
def test_insufficient_approval_blocks(): assert not may_commit(decision=make(approvals=1))
def test_state_change_makes_decision_stale(): assert is_stale(decision=make(current="sha256:new")) and not may_commit(decision=make(current="sha256:new"))
def test_rejected_cannot_commit(): assert not may_commit(decision=make("REJECTED"))
def test_governance_does_not_create_authority(): assert not creates_execution_authority(decision=make())
def test_deterministic(): assert make()==make()
