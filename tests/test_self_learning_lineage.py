import pytest
from gnosis.self_learning.knowledge import KnowledgeUpdate, apply_knowledge_update
from gnosis.self_learning.lineage import record_version, verify_lineage

def u(i):
    return apply_knowledge_update(KnowledgeUpdate(f"u{i}","flow-1","sha256:e",f"sha256:k{i}","common"))

def test_applied_update_gets_version():
    v=record_version(u(1))
    assert v.parent_version_id=="GENESIS"

def test_lineage_is_ordered():
    a=record_version(u(1)); b=record_version(u(2),parent_version_id=a.version_id)
    assert verify_lineage([a,b])==(True,())

def test_lineage_break_is_detected():
    a=record_version(u(1)); b=record_version(u(2),parent_version_id="sha256:wrong")
    ok,errors=verify_lineage([a,b])
    assert not ok
    assert errors


def test_knowledge_update_subject_must_match_lifecycle_subject() -> None:
    from gnosis.self_learning.lifecycle import verify_lifecycle
    from gnosis.self_learning.ledger import create_event

    events = []
    previous = None
    for stage in ("DATABASE","FINDING","PROPOSAL","VALIDATION","GOVERNANCE","EXECUTION_PLAN","RECEIPT"):
        event = create_event(stage, "flow-1", {"stage": stage}, previous)
        events.append(event)
        previous = event.event_digest
    lifecycle = verify_lifecycle(events, "flow-1")
    with pytest.raises(ValueError, match="subject"):
        from gnosis.self_learning.knowledge import propose_knowledge_update
        propose_knowledge_update(
            subject_id="flow-2",
            evidence_digest=events[-1].event_digest,
            knowledge={"k":"v"},
            lifecycle=lifecycle,
            scope="common",
            shareable=True,
        )
