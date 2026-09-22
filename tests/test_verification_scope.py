import pytest
from gnosis.core.types import State, Candidate, TestResult
from gnosis.core.verification_scope import VerificationScope, verification_scope_digest, verify_result_scope
from gnosis.core.rule_identity import rule_identity

def test_scope_binding_valid():
    c=Candidate(State({"x":1},(),1).state_id,State({"x":2},(),2),"test",1)
    rule=rule_identity("rule:1",{"predicate":"x>0"})
    s=VerificationScope(rule.rule_id,rule.rule_digest,c.candidate_id,"commit")
    verify_result_scope(c,TestResult(True,("ok",)),rule,"commit",verification_scope_digest(s),{"predicate":"x>0"})

def test_scope_rejects_rule_substitution():
    c=Candidate(State({"x":1},(),1).state_id,State({"x":2},(),2),"test",1)
    rule=rule_identity("rule:1",{"predicate":"x>0"})
    s=VerificationScope(rule.rule_id,rule.rule_digest,c.candidate_id,"commit")
    other=rule_identity("rule:2",{"predicate":"x>0"})
    with pytest.raises(ValueError):
        verify_result_scope(c,TestResult(True,("ok",)),other,"commit",verification_scope_digest(s),{"predicate":"x>0"})

def test_old_result_cannot_survive_rule_content_change():
    c=Candidate(State({"x":1},(),1).state_id,State({"x":2},(),2),"test",1)
    old=rule_identity("rule:1",{"predicate":"x>0"})
    s=VerificationScope(old.rule_id,old.rule_digest,c.candidate_id,"commit")
    digest=verification_scope_digest(s)
    new={"predicate":"x>=0"}
    with pytest.raises(ValueError,match="rule identity"):
        verify_result_scope(c,TestResult(True,("ok",)),old,"commit",digest,new)
