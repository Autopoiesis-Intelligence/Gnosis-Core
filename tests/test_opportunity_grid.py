from gnosis.self_learning.opportunity_grid import classify_opportunity,route_opportunity,may_form_contract,is_partner_isolated
def make(level="LOW_RELEVANCE",scope="general",status="ADMITTED"):
    return classify_opportunity(source_refs=("source:1",),evidence_refs=("e1",),value_level=level,scope=scope,rationale="evidence-backed value",status=status)
def test_low_routes_to_backlog(): assert route_opportunity(opportunity=make())=="GENERAL_BACKLOG"
def test_research_routes_to_research_contract(): assert route_opportunity(opportunity=make("RESEARCH_RELEVANT"))=="RESEARCH_CONTRACT"
def test_commercial_routes_to_partner_contract(): assert route_opportunity(opportunity=make("COMMERCIAL","partner:a"))=="PARTNER_CONTRACT"
def test_only_admitted_forms_contract(): assert not may_form_contract(opportunity=make(status="PROPOSED"))
def test_commercial_requires_partner_scope(): assert not is_partner_isolated(opportunity=make("COMMERCIAL","general"))
def test_deterministic(): assert make()==make()
