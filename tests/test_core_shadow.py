import pytest
from gnosis.core.rule_proposal import RuleProposal
from gnosis.core.shadow import evaluate_rule_proposal

def p(): return RuleProposal("rule:x","gap:x","finding:x",("e1",),"reason")

def test_shadow_pass_requires_all_checks():
    e=evaluate_rule_proposal(p(),state_id="s",checks=(("replay",True),("regression:old",True)))
    assert e.status=="PASS" and not e.regressions

def test_shadow_failure_blocks_evaluation():
    e=evaluate_rule_proposal(p(),state_id="s",checks=(("replay",True),("regression:old",False)))
    assert e.status=="FAIL"
    assert e.regressions==("regression:old",)

def test_non_proposal_cannot_enter_shadow():
    q=RuleProposal("rule:x","gap:x","finding:x",(),"r","COMMITTED")
    with pytest.raises(ValueError): evaluate_rule_proposal(q,state_id="s",checks=())
