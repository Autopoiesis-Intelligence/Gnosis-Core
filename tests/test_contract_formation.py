import pytest
from gnosis.self_learning.contract_formation import form_contract_candidate,may_issue,commercial_route_valid,creates_execution_authority
def make(level="LOW_RELEVANCE",scope="general",status="ADMITTED",fin=()):
    return form_contract_candidate(opportunity_id="opp:1",value_level=level,scope=scope,evidence_refs=("e1",),financial_refs=fin,status=status)
def test_low_forms_open_contract(): assert make().contract_kind=="GENERAL_OPEN" and may_issue(candidate=make())
def test_research_forms_legal_research_contract(): assert make("RESEARCH_RELEVANT").contract_kind=="RESEARCH_LEGAL"
def test_commercial_requires_financial_evidence():
    with pytest.raises(ValueError): make("COMMERCIAL","partner:a")
def test_commercial_routes_to_partner(): assert commercial_route_valid(candidate=make("COMMERCIAL","partner:a",fin=("fin:1",)))
def test_commercial_cannot_use_general_scope(): assert not commercial_route_valid(candidate=make("COMMERCIAL","general",fin=("fin:1",)))
def test_noncommercial_cannot_hide_financial_upgrade():
    with pytest.raises(ValueError): make("RESEARCH_RELEVANT",fin=("fin:1",))
def test_proposed_not_issued(): assert not may_issue(candidate=make(status="PROPOSED"))
def test_no_authority(): assert not creates_execution_authority(candidate=make())
def test_deterministic(): assert make()==make()
