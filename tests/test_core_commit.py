import pytest
from gnosis.core.governance import AuthorizationPackage
from gnosis.core.rule_proposal import RuleProposal
from gnosis.core.commit import commit

def a(): return AuthorizationPackage("auth:x","rule:x",("e1",),(),"shadow:x","AUTHORIZED")
def p(): return RuleProposal("rule:x","gap:x","finding:x",("e1",),"reason")

def test_authorized_commit_creates_new_state():
    r=commit(a(),p(),current_state_id="s1",new_state_id="s2",new_state={"x":1})
    assert r.record.status=="COMMITTED"
    assert r.record.previous_state_id=="s1"
    assert r.record.new_state_id=="s2"

def test_commit_rejects_unauthorized():
    aa=AuthorizationPackage("auth:x","rule:x",("e1",),(),"shadow:x","REJECTED")
    with pytest.raises(ValueError): commit(aa,p(),current_state_id="s1",new_state_id="s2",new_state={"x":1})

def test_commit_rejects_same_state_identity():
    with pytest.raises(ValueError): commit(a(),p(),current_state_id="s1",new_state_id="s1",new_state={"x":1})

def test_commit_requires_nonempty_state():
    with pytest.raises(ValueError): commit(a(),p(),current_state_id="s1",new_state_id="s2",new_state={})
