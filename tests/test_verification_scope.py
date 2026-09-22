import pytest
from gnosis.core.types import State, Candidate, TestResult
from gnosis.core.verification_scope import VerificationScope, verification_scope_digest, verify_result_scope

def test_scope_binding_valid():
    c=Candidate(State({"x":1},(),1).state_id,State({"x":2},(),2),"test",1)
    s=VerificationScope("rule:1",c.candidate_id,"commit")
    verify_result_scope(c,TestResult(True,("ok",)),s.rule_id,s.scope,verification_scope_digest(s))

def test_scope_rejects_rule_substitution():
    c=Candidate(State({"x":1},(),1).state_id,State({"x":2},(),2),"test",1)
    s=VerificationScope("rule:1",c.candidate_id,"commit")
    with pytest.raises(ValueError,match="scope digest"):
        verify_result_scope(c,TestResult(True,("ok",)),"rule:2",s.scope,verification_scope_digest(s))

def test_scope_rejects_nonpassing_result():
    c=Candidate(State({"x":1},(),1).state_id,State({"x":2},(),2),"test",1)
    s=VerificationScope("rule:1",c.candidate_id,"commit")
    with pytest.raises(ValueError,match="not passing"):
        verify_result_scope(c,TestResult(False,("bad",)),s.rule_id,s.scope,verification_scope_digest(s))
