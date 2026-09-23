import pytest

from gnosis.core import Candidate, TestResult, TransitionRecord
from gnosis.storage import StorageCorruptionError, connect, load_instance, persist_transition, save_instance, verify_audit_chain, verify_durable_graph
from gnosis.instances.instance import Instance
from gnosis.core import State


def test_same_transition_replay_is_idempotent():
    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)
    proposed = instance.engine.state.with_elements({"b": 2})
    candidate = Candidate(instance.engine.state.state_id, proposed, "replay-test")
    record = instance.engine.step(candidate)

    persist_transition(conn, instance, candidate, record, actor="test")
    transition_count = conn.execute("SELECT COUNT(*) FROM transitions").fetchone()[0]
    audit_count = conn.execute("SELECT COUNT(*) FROM audit_events WHERE transition_id IS NOT NULL").fetchone()[0]
    head = conn.execute("SELECT current_state_id FROM instances WHERE instance_id=?", (instance.instance_id,)).fetchone()[0]

    persist_transition(conn, instance, candidate, record, actor="test")

    assert conn.execute("SELECT COUNT(*) FROM transitions").fetchone()[0] == transition_count
    assert conn.execute("SELECT COUNT(*) FROM audit_events WHERE transition_id IS NOT NULL").fetchone()[0] == audit_count
    assert conn.execute("SELECT current_state_id FROM instances WHERE instance_id=?", (instance.instance_id,)).fetchone()[0] == head
    verify_durable_graph(conn)
    assert verify_audit_chain(conn)[0] == 2


def test_same_transition_id_with_conflicting_content_is_rejected():
    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)
    proposed = instance.engine.state.with_elements({"b": 2})
    candidate = Candidate(instance.engine.state.state_id, proposed, "replay-test")
    record = instance.engine.step(candidate)
    persist_transition(conn, instance, candidate, record, actor="test")

    conflicting = TransitionRecord(
        from_state_id=record.from_state_id,
        to_state_id=record.to_state_id,
        candidate_id=record.candidate_id,
        test_result=TestResult(False, ("conflicting",)),
        accepted=False,
        reason="conflicting replay",
        test_rule_id=record.test_rule_id,
    )
    with pytest.raises((ValueError, StorageCorruptionError)):
        persist_transition(conn, candidate= candidate, instance=instance, record=conflicting, actor="test")


def test_same_accepted_transition_replay_cannot_apply_changed_budget_snapshot():
    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)
    proposed = instance.engine.state.with_elements({"b": 2})
    candidate = Candidate(instance.engine.state.state_id, proposed, "budget-replay")
    record = instance.engine.step(candidate)

    persist_transition(conn, instance, candidate, record, actor="test")
    before = conn.execute(
        "SELECT current_state_id,budget_total,budget_spent FROM instances WHERE instance_id=?",
        (instance.instance_id,),
    ).fetchone()

    # Deliberately diverge the caller's in-memory budget after the durable commit.
    instance.engine.budget.spent += 999

    persist_transition(conn, instance, candidate, record, actor="replay")

    after = conn.execute(
        "SELECT current_state_id,budget_total,budget_spent FROM instances WHERE instance_id=?",
        (instance.instance_id,),
    ).fetchone()
    assert after == before
    assert conn.execute("SELECT COUNT(*) FROM transitions").fetchone()[0] == 1
    assert conn.execute(
        "SELECT COUNT(*) FROM audit_events WHERE transition_id IS NOT NULL"
    ).fetchone()[0] == 1
    verify_durable_graph(conn)


def test_same_transition_id_with_conflicting_from_state_is_rejected() -> None:
    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)
    proposed = instance.engine.state.with_elements({"b": 2})
    candidate = Candidate(instance.engine.state.state_id, proposed, "replay-parent-conflict")
    record = instance.engine.step(candidate)
    persist_transition(conn, instance, candidate, record, actor="test")

    conflicting = TransitionRecord(
        from_state_id="different-parent",
        to_state_id=record.to_state_id,
        candidate_id=record.candidate_id,
        test_result=record.test_result,
        accepted=record.accepted,
        reason=record.reason,
        test_rule_id=record.test_rule_id,
    )
    with pytest.raises((ValueError, StorageCorruptionError), match="candidate parent does not match transition source|conflicting transition replay|stale instance head"):
        persist_transition(conn, instance=instance, candidate=candidate, record=conflicting, actor="test")

    assert conn.execute("SELECT COUNT(*) FROM transitions").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM audit_events WHERE transition_id IS NOT NULL").fetchone()[0] == 1
    assert verify_audit_chain(conn)[0] == 2
    verify_durable_graph(conn)


def test_exact_transition_replay_after_reopen_is_idempotent_across_delivery_actor() -> None:
    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)
    proposed = instance.engine.state.with_elements({"b": 2})
    candidate = Candidate(instance.engine.state.state_id, proposed, "restart-replay")
    record = instance.engine.step(candidate)
    persist_transition(conn, instance, candidate, record, actor="worker-a")
    db_path = conn.execute("PRAGMA database_list").fetchone()[2]
    conn.close()

    reopened = connect(db_path)
    recovered = load_instance(reopened, instance.instance_id)
    persist_transition(reopened, recovered, candidate, record, actor="worker-b")

    assert reopened.execute("SELECT COUNT(*) FROM transitions").fetchone()[0] == 1
    assert reopened.execute("SELECT COUNT(*) FROM audit_events WHERE transition_id IS NOT NULL").fetchone()[0] == 1
    audit = reopened.execute(
        "SELECT actor,action,result,transition_id FROM audit_events WHERE transition_id=?",
        (record.transition_id,),
    ).fetchone()
    assert tuple(audit) == ("worker-a", "transition.commit", "accepted", record.transition_id)
    assert recovered.engine.state.state_id == record.to_state_id
    verify_durable_graph(reopened)
    reopened.close()


def test_replay_same_transition_id_after_restart_with_changed_candidate_is_rejected() -> None:
    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)
    candidate = Candidate(instance.engine.state.state_id, instance.engine.state.with_elements({"b": 2}), "corruption-replay")
    record = instance.engine.step(candidate)
    persist_transition(conn, instance, candidate, record, actor="worker-a")
    db_path = conn.execute("PRAGMA database_list").fetchone()[2]
    conn.close()

    reopened = connect(db_path)
    recovered = load_instance(reopened, instance.instance_id)
    corrupted_candidate = Candidate(record.from_state_id, State(elements={"tampered": True}), candidate.origin, candidate.seed)
    with pytest.raises(StorageCorruptionError, match="candidate|conflicting|mismatch"):
        persist_transition(reopened, recovered, corrupted_candidate, record, actor="worker-b")

    assert reopened.execute("SELECT COUNT(*) FROM transitions").fetchone()[0] == 1
    assert reopened.execute("SELECT COUNT(*) FROM audit_events WHERE transition_id IS NOT NULL").fetchone()[0] == 1
    verify_durable_graph(reopened)
    reopened.close()


def test_replay_detects_tampered_persisted_state_before_idempotent_acceptance():
    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)
    candidate = Candidate(
        instance.engine.state.state_id,
        instance.engine.state.with_elements({"b": 2}),
        "persisted-state-tamper",
    )
    record = instance.engine.step(candidate)
    persist_transition(conn, instance, candidate, record, actor="worker-a")

    conn.execute(
        "UPDATE states SET payload=? WHERE state_id=?",
        ('{"elements":{"tampered":true},"version":1}', record.to_state_id),
    )
    conn.commit()

    with pytest.raises(StorageCorruptionError, match="state hash mismatch"):
        load_instance(conn, instance.instance_id)

    assert verify_audit_chain(conn)[0] == 1

    assert conn.execute("SELECT COUNT(*) FROM transitions").fetchone()[0] == 1
    assert conn.execute(
        "SELECT COUNT(*) FROM audit_events WHERE transition_id IS NOT NULL"
    ).fetchone()[0] == 1
    conn.close()
