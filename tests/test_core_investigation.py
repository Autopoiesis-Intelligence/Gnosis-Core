import pytest
from gnosis.core.gap import GapHypothesis
from gnosis.core.reflection import ReflectionFinding
from gnosis.core.investigation import Investigation, Counterexample, admit_counterexample

def finding():
    return ReflectionFinding.from_gap(GapHypothesis("gap:x",("e1","e2"),"diagnostic","x",(),()))

def test_finding_creates_required_variation_investigation():
    i=Investigation.from_finding(finding())
    assert i.required_variations==("state","candidate","execution","source")
    assert i.status=="OPEN"

def test_counterexample_requires_matching_finding_and_evidence():
    i=Investigation.from_finding(finding())
    with pytest.raises(ValueError): admit_counterexample(i,Counterexample("c","finding:other","x",("e",)))
    with pytest.raises(ValueError): admit_counterexample(i,Counterexample("c","finding:x","x"))
    assert admit_counterexample(i,Counterexample("c","finding:x","x",("e3",))).status=="ADMITTED"
