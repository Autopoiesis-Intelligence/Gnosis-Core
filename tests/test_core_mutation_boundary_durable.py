from gnosis.core import Candidate, State, TestResult, TransitionRecord
from gnosis.instances.instance import Instance
from gnosis.storage.repositories import _persist_transition, load_transition_records, verify_durable_graph


def test_rejected_transition_is_durable_and_recoverable():
    conn = __import__("gnosis.storage", fromlist=["connect"]).connect()
    instance = Instance.create_root("contract-test", State(elements={"x": 1}))
    __import__("gnosis.storage", fromlist=["save_instance"]).save_instance(conn, instance)
    parent = instance.engine.state
    candidate = Candidate(parent.state_id, parent.with_elements({"x": 2}), "rejected-candidate")
    record = TransitionRecord(
        parent.state_id,
        candidate.proposed_state.state_id,
        candidate.candidate_id,
        TestResult(False, ("invariant-failed",)),
        False,
        "rejected",
        "contract",
    )
    _persist_transition(conn, instance, candidate, record, actor="contract-test")
    loaded = __import__("gnosis.storage", fromlist=["load_instance"]).load_instance(
        conn, instance.instance_id
    )
    assert loaded.engine.state.state_id == parent.state_id
    persisted = load_transition_records(conn, instance.instance_id)
    assert len(persisted) == 1
    assert persisted[0].transition_id == record.transition_id
    audit = conn.execute(
        "SELECT action,result,transition_id FROM audit_events WHERE transition_id=?",
        (record.transition_id,),
    ).fetchone()
    assert tuple(audit) == ("transition.reject", "rejected", record.transition_id)
    verify_durable_graph(conn)
    conn.close()
