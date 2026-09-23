from gnosis.self_learning.ledger import create_event
from gnosis.self_learning.lifecycle import verify_lifecycle

def make_flow():
    events=[]
    previous="GENESIS"
    for i,typ in enumerate(("DATABASE","FINDING","PROPOSAL","VALIDATION","GOVERNANCE","EXECUTION_PLAN","RECEIPT")):
        e=create_event(typ,"flow-1",{"i":i},previous)
        events.append(e); previous=e.event_digest
    return events

def test_complete_lifecycle():
    result=verify_lifecycle(make_flow(),"flow-1")
    assert result.complete is True
    assert result.missing == ()

def test_missing_stage_is_reported():
    events=make_flow()
    result=verify_lifecycle([e for e in events if e.event_type!="RECEIPT"],"flow-1")
    assert result.complete is False
    assert result.missing == ("RECEIPT",)

def test_order_violation_is_reported():
    events=make_flow()
    swapped=list(events); swapped[4],swapped[5]=swapped[5],swapped[4]
    result=verify_lifecycle(swapped,"flow-1")
    assert result.complete is False
    assert any(x.startswith("ORDER_VIOLATION") for x in result.errors)


def test_duplicate_required_stage_is_rejected() -> None:
    events=make_flow()
    duplicate=create_event("FINDING","flow-1",{"i":"duplicate"},events[1].event_digest)
    result=verify_lifecycle([events[0],events[1],duplicate,*events[2:]],"flow-1")
    assert result.complete is False
    assert any(x.startswith("DUPLICATE_STAGE:FINDING") for x in result.errors)
