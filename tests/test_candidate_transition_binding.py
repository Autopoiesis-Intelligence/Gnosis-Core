import pytest
from gnosis.core.types import State, Candidate, TransitionRecord, TestResult
from gnosis.core.candidate_binding import candidate_binding_digest
from gnosis.core.candidate_transition_binding import verify_candidate_transition_binding

def make():
    p=State({"x":1},(),1); proposed=State({"x":2},(),2)
    c=Candidate(p.state_id,proposed,"test",1)
    t=TransitionRecord(p.state_id,proposed.state_id,c.candidate_id,TestResult(True,("ok",)),True,"accepted","rule:1")
    return p,proposed,c,t,candidate_binding_digest(c,p)

def test_candidate_transition_binding_valid():
    p,_,c,t,d=make(); verify_candidate_transition_binding(c,p,t,d)

@pytest.mark.parametrize("mutate",["candidate","parent","proposed"])
def test_candidate_transition_binding_rejects_mismatch(mutate):
    p,proposed,c,t,d=make()
    if mutate=="candidate":
        t=TransitionRecord(t.from_state_id,t.to_state_id,"other",t.test_result,t.accepted,t.reason,t.test_rule_id)
    elif mutate=="parent":
        p=State({"x":9},(),1)
    else:
        t=TransitionRecord(t.from_state_id,"other",t.candidate_id,t.test_result,t.accepted,t.reason,t.test_rule_id)
    with pytest.raises(ValueError):
        verify_candidate_transition_binding(c,p,t,d)
