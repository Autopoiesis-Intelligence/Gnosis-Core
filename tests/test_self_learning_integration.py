import pytest
from gnosis.self_learning.lineage import KnowledgeVersion
from gnosis.self_learning.promotion import propose_promotion, decide_promotion
from gnosis.self_learning.integration import create_integration_record, mark_executed

def accepted():
    v=KnowledgeVersion("sha256:v","u","flow","common","sha256:k","GENESIS")
    p=propose_promotion(v,evidence_refs=("sha256:e",),reason="generalizable")
    return decide_promotion(p,decision="ACCEPTED",reviewer="r1")

def test_only_accepted_promotion_can_integrate():
    r=create_integration_record(accepted(),action="merge-approved-knowledge")
    assert r.status=="PROPOSED"

def test_rejected_promotion_cannot_integrate():
    v=KnowledgeVersion("sha256:v","u","flow","common","sha256:k","GENESIS")
    p=propose_promotion(v,evidence_refs=("sha256:e",),reason="x")
    p=decide_promotion(p,decision="REJECTED",reviewer="r1")
    with pytest.raises(ValueError): create_integration_record(p,action="merge")

def test_execution_requires_receipt():
    r=create_integration_record(accepted(),action="merge-approved-knowledge")
    done=mark_executed(r,receipt_id="receipt-1")
    assert done.status=="EXECUTED"
