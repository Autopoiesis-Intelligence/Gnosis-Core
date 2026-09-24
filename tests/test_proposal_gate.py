import pytest
from gnosis.self_learning.proposal_gate import decide_proposal,may_activate,decision_binds_proposal,creates_execution_authority
def make(dec="ACCEPT"):
    return decide_proposal(proposal_id="proposal:1",proposal_digest="sha256:p",actor_ref="reviewer:1",decision=dec,reason="reviewed evidence")
def test_accept_activates_proposal(): assert may_activate(proposal_status="PROPOSED",decision=make())
def test_reject_does_not_activate(): assert not may_activate(proposal_status="PROPOSED",decision=make("REJECT"))
def test_decision_binds_exact_proposal(): assert decision_binds_proposal(decision=make(),proposal_id="proposal:1",proposal_digest="sha256:p")
def test_mismatch_breaks_binding(): assert not decision_binds_proposal(decision=make(),proposal_id="proposal:2",proposal_digest="sha256:p")
def test_no_authority(): assert not creates_execution_authority(decision=make())
def test_invalid_decision():
    with pytest.raises(ValueError): make("APPROVE")
def test_deterministic(): assert make()==make()
