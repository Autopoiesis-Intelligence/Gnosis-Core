import pytest
from gnosis.self_learning.lineage import KnowledgeVersion
from gnosis.self_learning.promotion import propose_promotion, decide_promotion

def version():
    return KnowledgeVersion("sha256:v","u","flow-1","common","sha256:k","GENESIS")

def test_promotion_requires_evidence():
    with pytest.raises(ValueError):
        propose_promotion(version(),evidence_refs=(),reason="generalizable")

def test_promotion_is_not_authority():
    p=propose_promotion(version(),evidence_refs=("sha256:e",),reason="generalizable")
    assert p.status=="PROPOSED"
    assert p.authority=="promotion-proposal-only"

def test_governance_decision_is_explicit():
    p=propose_promotion(version(),evidence_refs=("sha256:e",),reason="generalizable")
    a=decide_promotion(p,decision="ACCEPTED",reviewer="reviewer-1")
    assert a.status=="ACCEPTED"
