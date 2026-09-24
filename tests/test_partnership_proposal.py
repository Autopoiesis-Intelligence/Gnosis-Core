import pytest
from gnosis.self_learning.partnership_proposal import generate_partnership_proposal,may_submit,creates_contract,grants_execution_authority
def make(eligible=True,status="PROPOSED"): return generate_partnership_proposal(opportunity_id="opp:1",partner_scope="partner:a",core_scope="minimal-core",expected_result="validated partner core",constraints=("no execution authority",),evidence_refs=("e1",),commercial_decision_id="cd:1",commercial_eligible=eligible,status=status)
def test_eligible_proposal_can_submit(): assert may_submit(proposal=make())
def test_gate_required():
 with pytest.raises(ValueError): make(False)
def test_constraints_required():
 with pytest.raises(ValueError): generate_partnership_proposal(opportunity_id="o",partner_scope="partner:a",core_scope="c",expected_result="r",constraints=(),evidence_refs=("e",),commercial_decision_id="d",commercial_eligible=True)
def test_wrong_scope_blocks():
 with pytest.raises(ValueError): generate_partnership_proposal(opportunity_id="o",partner_scope="research",core_scope="c",expected_result="r",constraints=("x",),evidence_refs=("e",),commercial_decision_id="d",commercial_eligible=True)
def test_no_contract_creation(): assert not creates_contract(proposal=make())
def test_no_execution_authority(): assert not grants_execution_authority(proposal=make())
def test_deterministic(): assert make()==make()
