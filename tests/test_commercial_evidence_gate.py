import pytest
from gnosis.self_learning.commercial_evidence_gate import assess_commercial_evidence,may_promote,creates_contract
def make(status="ADMITTED",scope="partner:a"): return assess_commercial_evidence(opportunity_id="opp:1",evidence_refs=("market:e1",),financial_refs=("financial:f1",),partner_scope=scope,rationale="documented commercial evidence",status=status)
def test_admitted_commercial_evidence_allows_promotion(): assert may_promote(decision=make())
def test_proposed_does_not_promote(): assert not may_promote(decision=make("PROPOSED"))
def test_partner_scope_required():
 with pytest.raises(ValueError): make(scope="research")
def test_financial_evidence_required():
 with pytest.raises(ValueError): assess_commercial_evidence(opportunity_id="o",evidence_refs=("e",),financial_refs=(),partner_scope="partner:a",rationale="r")
def test_general_evidence_required():
 with pytest.raises(ValueError): assess_commercial_evidence(opportunity_id="o",evidence_refs=(),financial_refs=("f",),partner_scope="partner:a",rationale="r")
def test_no_contract_creation(): assert not creates_contract(decision=make())
def test_deterministic(): assert make()==make()
