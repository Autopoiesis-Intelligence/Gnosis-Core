import pytest
from gnosis.core.types import State, Candidate
from gnosis.core.state_identity_contract import identify_state, validate_candidate_parent
from gnosis.core.state_identity import state_digest

def test_state_identity_layers_are_distinct_contracts():
    s=State({"x":1},(),3); i=identify_state(s)
    assert i.state_id==s.state_id
    assert i.content_id==s.content_id
    assert i.state_digest==state_digest(s)

def test_candidate_binds_to_parent_identity_and_digest():
    parent=State({"x":1},(),1)
    c=Candidate(parent.state_id,State({"x":2},(),2),"test",1)
    validate_candidate_parent(c,parent,state_digest(parent))

def test_candidate_rejects_wrong_parent_id():
    parent=State({"x":1},(),1); c=Candidate("wrong",State({"x":2},(),2),"test",1)
    with pytest.raises(ValueError,match="parent_state_id"):
        validate_candidate_parent(c,parent,state_digest(parent))

def test_candidate_rejects_wrong_parent_digest():
    parent=State({"x":1},(),1); c=Candidate(parent.state_id,State({"x":2},(),2),"test",1)
    with pytest.raises(ValueError,match="digest"):
        validate_candidate_parent(c,parent,"wrong");
