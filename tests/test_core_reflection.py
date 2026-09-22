import pytest
from gnosis.core.gap import GapHypothesis
from gnosis.core.reflection import ReflectionFinding

def gap(status="HYPOTHESIS", refs=("e1","e2")):
    return GapHypothesis("gap:x",refs,"diagnostic_pattern","Repeated pattern",("verified",),())

def test_gap_enters_reflection_without_mutating_core():
    f=ReflectionFinding.from_gap(gap())
    assert f.gap_id=="gap:x"
    assert f.status=="OPEN"
    assert f.source_records==("e1","e2")

def test_non_hypothesis_cannot_enter_reflection():
    g=gap(); g=GapHypothesis(g.gap_id,g.source_records,g.trigger_kind,g.description,g.conditions,g.counterevidence,"COMMITTED")
    with pytest.raises(ValueError): ReflectionFinding.from_gap(g)
