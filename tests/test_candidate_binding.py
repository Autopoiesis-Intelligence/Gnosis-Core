import pytest
from gnosis.core.types import State, Candidate
from gnosis.core.candidate_binding import candidate_binding_digest, verify_candidate_binding

def test_candidate_binding_is_valid_for_original_parent():
    a=State({"x":1},(),1); c=Candidate(a.state_id,State({"x":2},(),2),"test",1)
    d=candidate_binding_digest(c,a)
    assert verify_candidate_binding(c,a,d)

def test_candidate_cannot_rebind_to_different_parent():
    a=State({"x":1},(),1); b=State({"x":9},(),1)
    c=Candidate(a.state_id,State({"x":2},(),2),"test",1)
    d=candidate_binding_digest(c,a)
    assert not verify_candidate_binding(c,b,d)

def test_candidate_binding_changes_when_parent_content_changes():
    a=State({"x":1},(),1); b=State({"x":2},(),1)
    c=Candidate(a.state_id,State({"x":3},(),2),"test",1)
    assert candidate_binding_digest(c,a)!=candidate_binding_digest(c,b)
