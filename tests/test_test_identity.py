import pytest
from gnosis.core.types import State, Candidate, TransitionRecord, TestResult
from gnosis.core.test_identity import test_result_digest, verify_test_transition_binding

def make(result=None):
    p=State({"x":1},(),1); q=State({"x":2},(),2); c=Candidate(p.state_id,q,"test",1)
    result=result or TestResult(True,("ok",))
    t=TransitionRecord(p.state_id,q.state_id,c.candidate_id,result,result.passed,"accepted" if result.passed else "rejected","rule:1")
    return c,result,t

def test_test_result_binding_valid():
    c,r,t=make(); verify_test_transition_binding(c,r,t,test_result_digest(r))

def test_failing_result_cannot_be_accepted():
    c,r,_=make(TestResult(False,("failure",)))
    t=TransitionRecord("s1","s2",c.candidate_id,r,True,"accepted","rule:1")
    with pytest.raises(ValueError,match="failing"):
        verify_test_transition_binding(c,r,t,test_result_digest(r))

def test_result_tamper_is_detected():
    c,r,t=make(); verify_test_transition_binding(c,r,t,test_result_digest(r))
    with pytest.raises(ValueError,match="digest"):
        verify_test_transition_binding(c,TestResult(True,("tampered",)),t,test_result_digest(r))
