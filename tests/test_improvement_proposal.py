import pytest
from gnosis.self_learning.improvement_proposal import form_improvement_proposal,may_review,creates_execution_authority

def make(level="RESEARCH_RELEVANT",scope="research"):
    return form_improvement_proposal(memory_entry_id="memory:1",cycle_id="cycle:1",input_id="input:1",opportunity_id="opp:1",contract_id="contract:1",scope=scope,value_level=level,evidence_refs=("e1","e2"),financial_refs=("fin:1",) if level=="COMMERCIAL" else (),rationale="evidence-backed improvement",expected_result="validated improvement",acceptance_conditions=("replay",),unresolved_gaps=("runtime",))

def test_complete_provenance_is_bound(): assert make().proposal_id.startswith("sha256:") and may_review(proposal=make())
def test_missing_evidence_blocks():
    with pytest.raises(ValueError): form_improvement_proposal(memory_entry_id="m",cycle_id="c",input_id="i",opportunity_id="o",contract_id="x",scope="research",value_level="RESEARCH_RELEVANT",evidence_refs=(),rationale="r",expected_result="e",acceptance_conditions=("a",))
def test_commercial_requires_partner_and_financial():
    with pytest.raises(ValueError): make("COMMERCIAL","research")
def test_commercial_valid(): assert may_review(proposal=make("COMMERCIAL","partner:a"))
def test_no_authority(): assert not creates_execution_authority(proposal=make())
def test_deterministic(): assert make()==make()
