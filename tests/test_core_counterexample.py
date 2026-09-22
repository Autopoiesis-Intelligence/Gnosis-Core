import pytest
from gnosis.core.gap import GapHypothesis
from gnosis.core.investigation import Counterexample
from gnosis.core.counterexample import verify_counterexample,reassess_gap

def ce(status="ADMITTED"):
    return Counterexample("c","finding:x","counter",("e3",),status)

def test_only_admitted_counterexample_can_be_verified():
    with pytest.raises(ValueError): verify_counterexample(ce("PROPOSED"),refutes=True,reason="r")
    assert verify_counterexample(ce(),refutes=True,reason="r").result=="REFUTES"

def test_refutation_reassesses_gap():
    g=GapHypothesis("gap:x",("e1","e2"),"diagnostic","x")
    v=verify_counterexample(ce(),refutes=True,reason="r")
    r=reassess_gap(g,"finding:x",(v,))
    assert r.result=="REFUTED"

def test_non_refuting_evidence_keeps_gap_unresolved():
    g=GapHypothesis("gap:x",("e1","e2"),"diagnostic","x")
    v=verify_counterexample(ce(),refutes=False,reason="r")
    assert reassess_gap(g,"finding:x",(v,)).result=="UNRESOLVED"
