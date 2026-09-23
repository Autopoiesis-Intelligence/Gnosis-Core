import pytest
from gnosis.self_learning.ledger import create_event
from gnosis.self_learning.lifecycle import verify_lifecycle
from gnosis.self_learning.knowledge import propose_knowledge_update, apply_knowledge_update

def flow():
    events=[]; prev="GENESIS"
    for i,typ in enumerate(("DATABASE","FINDING","PROPOSAL","VALIDATION","GOVERNANCE","EXECUTION_PLAN","RECEIPT")):
        e=create_event(typ,"flow-1",{"i":i},prev); events.append(e); prev=e.event_digest
    return verify_lifecycle(events,"flow-1")

def test_verified_shareable_flow_can_propose_update():
    u=propose_knowledge_update(subject_id="flow-1",evidence_digest="sha256:e",knowledge={"rule":"x"},lifecycle=flow(),scope="common",shareable=True)
    assert u.status=="PROPOSED"
    assert apply_knowledge_update(u).status=="APPLIED"

def test_incomplete_flow_is_rejected():
    bad=flow()
    bad=type(bad)(False,"x",("RECEIPT",),("MISSING_STAGES:RECEIPT",))
    with pytest.raises(ValueError):
        propose_knowledge_update(subject_id="x",evidence_digest="e",knowledge={},lifecycle=bad,scope="common",shareable=True)

def test_private_evidence_is_rejected():
    with pytest.raises(PermissionError):
        propose_knowledge_update(subject_id="flow-1",evidence_digest="e",knowledge={},lifecycle=flow(),scope="common",shareable=False)
