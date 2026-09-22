import pytest
from gnosis.core.rule_proposal import RuleProposal
from gnosis.core.shadow import ShadowEvaluation
from gnosis.core.governance import authorize

def p(): return RuleProposal("rule:x","gap:x","finding:x",("e1",),"reason")
def s(status="PASS", proposal_id="rule:x"): return ShadowEvaluation("shadow:x",proposal_id,"s",status,("replay",),())

def test_passing_shadow_authorizes_with_provenance():
    a=authorize(p(),s(),evidence_refs=("e1","e2"),counterexample_refs=("c1",),limitations=("scope:s",))
    assert a.decision=="AUTHORIZED"
    assert a.shadow_evaluation_id=="shadow:x"

def test_failed_shadow_cannot_authorize():
    with pytest.raises(ValueError): authorize(p(),s("FAIL"),evidence_refs=("e1",))

def test_identity_mismatch_cannot_authorize():
    with pytest.raises(ValueError): authorize(p(),s(proposal_id="rule:y"),evidence_refs=("e1",))

def test_missing_evidence_cannot_authorize():
    with pytest.raises(ValueError): authorize(p(),s(),evidence_refs=())
