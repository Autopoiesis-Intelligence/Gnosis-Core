import pytest
from gnosis.self_learning.contract_generation import generate_contract,binds_proposal,may_execute
def make(status="READY_FOR_EXECUTION",accepted=True): return generate_contract(proposal_id="p:1",proposal_digest="sha256:p",collaboration_type="COMMERCIAL_PARTNERSHIP",scope="partner:a",rights_profile="commercial",acceptance_criteria=("tests pass",),evidence_requirements=("e1",),transfer_boundary="minimal-core-only",accepted=accepted,status=status)
def test_accepted_proposal_generates_contract(): assert may_execute(contract=make())
def test_rejected_proposal_blocks():
 with pytest.raises(ValueError): make(accepted=False)
def test_exact_proposal_binding():
 c=make(); assert binds_proposal(contract=c,proposal_id="p:1",proposal_digest="sha256:p")
def test_digest_mismatch():
 c=make(); assert not binds_proposal(contract=c,proposal_id="p:1",proposal_digest="sha256:x")
def test_criteria_required():
 with pytest.raises(ValueError): generate_contract(proposal_id="p",proposal_digest="d",collaboration_type="OPEN_NONCOMMERCIAL",scope="s",rights_profile="r",acceptance_criteria=(),evidence_requirements=("e",),transfer_boundary="b")
def test_draft_not_executable(): assert not may_execute(contract=make("DRAFT"))
def test_deterministic(): assert make()==make()
