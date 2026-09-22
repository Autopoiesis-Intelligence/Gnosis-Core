import pytest
from gnosis.core.gap import GapHypothesis
from gnosis.core.counterexample import ReflectionReassessment
from gnosis.core.rule_proposal import qualify_supported,make_rule_proposal

def g(): return GapHypothesis("gap:x",("e1","e2"),"diagnostic","x")

def test_supported_can_create_rule_proposal():
    r=qualify_supported(ReflectionReassessment("gap:x","finding:x","UNRESOLVED",(),True),g())
    assert r.result=="SUPPORTED"
    assert make_rule_proposal(r,g()).status=="PROPOSED"

def test_refuted_cannot_create_rule_proposal():
    r=ReflectionReassessment("gap:x","finding:x","REFUTED",("c",),False)
    with pytest.raises(ValueError): make_rule_proposal(r,g())

def test_identity_is_required():
    with pytest.raises(ValueError):
        qualify_supported(ReflectionReassessment("gap:y","finding:y","UNRESOLVED",(),True),g())
