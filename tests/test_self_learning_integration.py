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
        mark_executed(r, receipt="forged-receipt", request=_execution_fixture()[0])


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
        mark_executed(tampered, receipt=receipt, request=_execution_fixture()[0])


def test_e7_59_arbitrary_receipt_is_rejected():
    r=create_integration_record(accepted(), action="merge-approved-knowledge")
    with pytest.raises(TypeError, match="authenticated ExecutionReceipt"):
        mark_executed(r, receipt="forged-receipt", request=_execution_fixture()[0])


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
        mark_executed(r, receipt=receipt, request=_execution_fixture()[0])


def test_e7_60_real_execution_receipt_identity_is_not_integration_id():
    from gnosis.evolution.provenance import build_provenance
    from gnosis.reflection.authority import ExecutionReceipt
    r=create_integration_record(accepted(), action="merge-approved-knowledge")
    observations={"result":"ok"}
    import hashlib, json
    evidence_digest=hashlib.sha256(json.dumps(observations,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    p=build_provenance(
        candidate_id="candidate:1",
        parent_state_id="state:parent",
        parent_state_digest="sha256:parent",
        proposed_state_digest="sha256:result",
        observations=observations,
        evidence_digest=evidence_digest,
        evaluation_status="PASS",
        shadow_status="PASS",
        invariant_status="PASS",
        governance_decision="ACCEPT",
    )
    receipt=ExecutionReceipt(
        execution_id=p.execution_id,
        provenance_id=p.provenance_id,
        evolution_identity=p.evolution_identity,
        parent_state_digest=p.parent_state_digest,
        resulting_state_digest=p.proposed_state_digest,
        candidate_binding_digest=p.candidate_binding_digest,
    )
    assert receipt.execution_id != r.integration_id
    with pytest.raises(ValueError, match="execution receipt"):
        mark_executed(r, receipt=receipt, request=_execution_fixture()[0])


def _execution_fixture():
    from types import SimpleNamespace
    from gnosis.reflection.authority import ExecutionAuthorization, ExecutionCommitRequest, ExecutionIntentSnapshot, ExecutionReceipt
    p=SimpleNamespace(
        provenance_id="prov:1", execution_id="exec:1",
        parent_state_id="state:parent", parent_state_digest="sha256:parent",
        evolution_identity="evolution:1", candidate_binding_digest="sha256:binding",
        proposed_state_digest="sha256:result", proposed_state_content_id="sha256:content",
    )
    auth=ExecutionAuthorization("prov:1",True,"evolution:1","approval:1")
    snapshot=ExecutionIntentSnapshot.from_provenance(p)
    request=ExecutionCommitRequest(auth,snapshot,"prov:1","evolution:1",p)
    receipt=ExecutionReceipt("exec:1","prov:1","evolution:1","sha256:parent","sha256:result","sha256:binding")
    return request, receipt


def test_e7_60_matching_receipt_and_authorized_request_are_accepted():
    r=create_integration_record(accepted(), action="merge-approved-knowledge")
    request, receipt=_execution_fixture()
    done=mark_executed(r, receipt=receipt, request=request)
    assert done.status=="EXECUTED"
    assert done.execution_id=="exec:1"
    assert done.provenance_id=="prov:1"


def test_e7_60_receipt_from_other_execution_is_rejected():
    r=create_integration_record(accepted(), action="merge-approved-knowledge")
    request, receipt=_execution_fixture()
    from dataclasses import replace
    foreign=replace(receipt, execution_id="exec:foreign")
    with pytest.raises(ValueError, match="authorized evolution"):
        mark_executed(r, receipt=foreign, request=request)
