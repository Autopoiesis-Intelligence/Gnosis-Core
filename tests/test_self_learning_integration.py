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

def test_execution_requires_authenticated_receipt():
    r=create_integration_record(accepted(),action="merge-approved-knowledge")
    with pytest.raises(TypeError, match="authenticated ExecutionReceipt"):
        mark_executed(r, receipt="forged-receipt")


def test_tampered_integration_identity_is_rejected() -> None:
    from dataclasses import replace
    r=create_integration_record(accepted(), action="merge-approved-knowledge")
    tampered=replace(r, integration_id="sha256:tampered")
    from gnosis.reflection.authority import ExecutionReceipt
    receipt=ExecutionReceipt(
        execution_id=r.integration_id,
        provenance_id="sha256:p",
        evolution_identity="evolution:x",
        parent_state_digest="sha256:parent",
        resulting_state_digest="sha256:result",
        candidate_binding_digest="sha256:binding",
    )
    with pytest.raises(ValueError, match="integration identity"):
        mark_executed(tampered, receipt=receipt)


def test_e7_59_arbitrary_receipt_is_rejected():
    r=create_integration_record(accepted(), action="merge-approved-knowledge")
    with pytest.raises(TypeError, match="authenticated ExecutionReceipt"):
        mark_executed(r, receipt="forged-receipt")


def test_e7_59_receipt_identity_must_match_integration():
    r=create_integration_record(accepted(), action="merge-approved-knowledge")
    from gnosis.reflection.authority import ExecutionReceipt
    receipt=ExecutionReceipt(
        execution_id="sha256:forged",
        provenance_id="sha256:p",
        evolution_identity="evolution:x",
        parent_state_digest="sha256:parent",
        resulting_state_digest="sha256:result",
        candidate_binding_digest="sha256:binding",
    )
    with pytest.raises(ValueError, match="execution receipt"):
        mark_executed(r, receipt=receipt)
