from gnosis.storage.repositories import _persist_transition

def _authorized_recover(conn, instance_id):
    digest = recovery_evidence_digest(conn, instance_id)
    authorization = RecoveryAuthorization(
        authorization_id="test-recovery", subject=instance_id,
        requested_by="test-principal", authority="test-governance",
        decision="allow", reason="test recovery",
        issued_at="2026-09-25T00:00:00Z", expires_at="2026-09-26T00:00:00Z",
        evidence_digest=digest,
    )
    return recover_instance(conn, instance_id, authorization, now="2026-09-25T12:00:00Z")


import json
import sqlite3
import threading

import pytest

from gnosis.core import Candidate, State, TestResult, TransitionRecord
from gnosis.instances.instance import Instance
from gnosis.instances.fork import fork_instance
from gnosis.storage import (
    SecretMaterialError,
    StorageCorruptionError,
    append_audit,
    connect,
    load_instance,
recover_instance,
    save_instance,
    verify_durable_graph,
)


def test_orphan_transition_is_rejected_by_schema():
    conn = connect()
    instance = Instance.create_root("u", State(elements={"a": 1}))
    save_instance(conn, instance)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO transitions(transition_id, instance_id, candidate_id, from_state_id, to_state_id, accepted, reasons, created_at) VALUES ('t', ?, NULL, ?, ?, 1, '[]', 'now')", (instance.instance_id, instance.engine.state.state_id, instance.engine.state.state_id))


def test_audit_event_replay_is_idempotent():
    conn = connect()
    first = append_audit(conn, actor="u", action="x", resource="r", result="ok", timestamp="fixed", event_key="request-1")
    second = append_audit(conn, actor="u", action="x", resource="r", result="ok", timestamp="fixed", event_key="request-1")
    assert first == second
    assert conn.execute("SELECT count(*) FROM audit_events").fetchone()[0] == 1


def test_conflicting_audit_replay_is_rejected():
    conn = connect()
    append_audit(conn, actor="u", action="x", resource="r", result="ok", event_key="request-1")
    with pytest.raises(StorageCorruptionError):
        append_audit(conn, actor="u", action="x", resource="other", result="ok", event_key="request-1")


def test_secret_bearing_state_is_rejected_before_write():
    conn = connect()
    instance = Instance.create_root("u", State(elements={"api_key": "do-not-store"}))
    with pytest.raises(SecretMaterialError):
        save_instance(conn, instance)
    assert conn.execute("SELECT count(*) FROM states").fetchone()[0] == 0


def test_budget_and_history_survive_restart():
    conn = connect()
    instance = Instance.create_root("u", State(elements={"a": 1}))
    save_instance(conn, instance)
    proposed = instance.engine.state.with_elements({"b": 2})
    candidate = Candidate(instance.engine.state.state_id, proposed, "test")
    record = instance.engine.step(candidate)
    _persist_transition(conn, instance, candidate, record, actor="u")
    recovered = load_instance(conn, instance.instance_id)
    assert recovered.engine.budget.spent == instance.engine.budget.spent
    assert verify_durable_graph(conn)[0] == 2


def test_head_without_transition_fails_graph_verification():
    conn = connect()
    instance = Instance.create_root("u", State(elements={"a": 1}))
    save_instance(conn, instance)
    # Valid state row but an unauthorized head move.
    proposed = instance.engine.state.with_elements({"b": 2})
    conn.execute("INSERT INTO states(state_id, version, payload, created_at) VALUES (?, ?, ?, ?)", (proposed.state_id, proposed.version, json.dumps({"elements": {"b": 2}, "version": proposed.version}, separators=(",", ":")), "now"))
    conn.execute("UPDATE instances SET current_state_id=? WHERE instance_id=?", (proposed.state_id, instance.instance_id))
    with pytest.raises(StorageCorruptionError):
        verify_durable_graph(conn)


@pytest.mark.parametrize("point", ["before_begin", "after_begin", "after_candidate", "after_transition", "after_audit", "after_head", "before_commit"])
def test_fault_injection_rolls_back_transition(point):
    conn = connect()
    instance = Instance.create_root("u", State(elements={"a": 1}))
    save_instance(conn, instance)
    original_state_id = instance.engine.state.state_id
    proposed = instance.engine.state.with_elements({"b": 2})
    candidate = Candidate(instance.engine.state.state_id, proposed, "test")
    record = instance.engine.step(candidate)
    with pytest.raises(RuntimeError, match="injected failure"):
        _persist_transition(conn, instance, candidate, record, actor="u", failure_at=point)
    assert load_instance(conn, instance.instance_id).engine.state.state_id == original_state_id
    assert verify_durable_graph(conn)[0] == 1


def test_recover_instance_runs_graph_validation():
    conn = connect()
    instance = Instance.create_root("u", State(elements={"a": 1}))
    save_instance(conn, instance)
    assert _authorized_recover(conn, instance.instance_id).instance_id == instance.instance_id


def test_after_commit_failure_leaves_committed_transition_durable():
    conn = connect()
    instance = Instance.create_root("u", State(elements={"a": 1}))
    save_instance(conn, instance)
    proposed = instance.engine.state.with_elements({"b": 2})
    candidate = Candidate(instance.engine.state.state_id, proposed, "test")
    record = instance.engine.step(candidate)
    with pytest.raises(RuntimeError, match="injected failure"):
        _persist_transition(conn, instance, candidate, record, actor="u", failure_at="after_commit")
    assert load_instance(conn, instance.instance_id).engine.state.state_id == proposed.state_id
    assert verify_durable_graph(conn)[0] == 2


def test_fork_after_restart_preserves_independent_heads_lineage_and_audit():
    conn = connect()
    root = Instance.create_root("u", State(elements={"root": 0}))
    save_instance(conn, root)
    a1 = root.engine.state.with_elements({"a1": 1})
    ca1 = Candidate(root.engine.state.state_id, a1, "root-step")
    ra1 = root.engine.step(ca1)
    _persist_transition(conn, root, ca1, ra1, actor="u")

    # Simulated restart: recover A at A1 before creating the fork.
    recovered_a = _authorized_recover(conn, root.instance_id)
    child = fork_instance(recovered_a)
    save_instance(conn, child)

    a2 = recovered_a.engine.state.with_elements({"a2": 2})
    ca2 = Candidate(recovered_a.engine.state.state_id, a2, "a-branch")
    ra2 = recovered_a.engine.step(ca2)
    _persist_transition(conn, recovered_a, ca2, ra2, actor="u")

    b1 = child.engine.state.with_elements({"b1": 1})
    cb1 = Candidate(child.engine.state.state_id, b1, "b-branch")
    rb1 = child.engine.step(cb1)
    _persist_transition(conn, child, cb1, rb1, actor="u")

    recovered_a2 = _authorized_recover(conn, recovered_a.instance_id)
    recovered_b1 = _authorized_recover(conn, child.instance_id)
    assert recovered_a2.engine.state.state_id == a2.state_id
    assert recovered_b1.engine.state.state_id == b1.state_id
    assert recovered_a2.parent_instance_id is None
    assert recovered_b1.parent_instance_id == recovered_a2.instance_id
    assert recovered_b1.generation == recovered_a2.generation + 1
    assert "a2" in recovered_a2.engine.state.elements
    assert "b1" in recovered_b1.engine.state.elements
    assert "b1" not in recovered_a2.engine.state.elements
    assert "a2" not in recovered_b1.engine.state.elements
    assert verify_durable_graph(conn)[0] == 5


def _transition(instance, key):
    proposed = instance.engine.state.with_elements({key: 1})
    candidate = Candidate(instance.engine.state.state_id, proposed, key)
    return candidate, instance.engine.step(candidate)


def test_a27_direct_persistence_stale_head_is_rejected():
    conn = connect()
    instance = Instance.create_root("u", State(elements={"a": 1}))
    save_instance(conn, instance)
    stale_instance = load_instance(conn, instance.instance_id)
    first_candidate, first_record = _transition(instance, "first")
    stale_candidate, stale_record = _transition(stale_instance, "stale")
    _persist_transition(conn, instance, first_candidate, first_record, actor="u")
    with pytest.raises(ValueError, match="stale instance head"):
        _persist_transition(conn, instance, stale_candidate, stale_record, actor="u")
    assert load_instance(conn, instance.instance_id).engine.state.state_id == first_candidate.proposed_state.state_id
    assert verify_durable_graph(conn)[0] == 2


def test_a31_fork_creation_failure_rolls_back_child(monkeypatch):
    conn = connect()
    parent = Instance.create_root("u", State(elements={"root": 0}))
    save_instance(conn, parent)
    child = fork_instance(parent)

    def fail_audit(*args, **kwargs):
        raise RuntimeError("injected fork audit failure")

    monkeypatch.setattr("gnosis.storage.repositories.append_audit", fail_audit)
    with pytest.raises(RuntimeError, match="injected fork audit failure"):
        save_instance(conn, child)
    assert conn.execute("SELECT 1 FROM instances WHERE instance_id=?", (child.instance_id,)).fetchone() is None
    assert _authorized_recover(conn, parent.instance_id).instance_id == parent.instance_id


def test_a33_lineage_cycle_fails_recovery():
    conn = connect()
    parent = Instance.create_root("u", State(elements={"root": 0}))
    save_instance(conn, parent)
    child = fork_instance(parent)
    save_instance(conn, child)
    conn.execute("PRAGMA foreign_keys=OFF")
    conn.execute("UPDATE instances SET parent_instance_id=?, generation=? WHERE instance_id=?", (child.instance_id, child.generation, child.instance_id))
    with pytest.raises(StorageCorruptionError, match="invalid fork lineage"):
        _authorized_recover(conn, child.instance_id)


def test_a34_generation_mismatch_fails_recovery():
    conn = connect()
    parent = Instance.create_root("u", State(elements={"root": 0}))
    save_instance(conn, parent)
    child = fork_instance(parent)
    save_instance(conn, child)
    conn.execute("UPDATE instances SET generation=? WHERE instance_id=?", (child.generation + 1, child.instance_id))
    with pytest.raises(StorageCorruptionError, match="invalid fork lineage"):
        _authorized_recover(conn, child.instance_id)


def test_a35_multiple_instances_interleaved_commits_keep_independent_heads():
    conn = connect()
    first = Instance.create_root("u", State(elements={"root": "first"}))
    second = Instance.create_root("u", State(elements={"root": "second"}))
    save_instance(conn, first)
    save_instance(conn, second)
    for instance, key in ((first, "first-next"), (second, "second-next"), (first, "first-final"), (second, "second-final")):
        candidate, record = _transition(instance, key)
        _persist_transition(conn, instance, candidate, record, actor="u")
    recovered_first = recover_instance(conn, first.instance_id)
    recovered_second = recover_instance(conn, second.instance_id)
    assert recovered_first.engine.state.elements["first-final"] == 1
    assert "second-final" not in recovered_first.engine.state.elements
    assert recovered_second.engine.state.elements["second-final"] == 1
    assert "first-final" not in recovered_second.engine.state.elements
    assert verify_durable_graph(conn)[0] == 6


def test_a36_concurrent_same_head_allows_one_accepted_transition(tmp_path):
    path = tmp_path / "same-head.sqlite"
    setup = connect(path)
    instance = Instance.create_root("u", State(elements={"root": 0}))
    save_instance(setup, instance)
    writer_a = load_instance(setup, instance.instance_id)
    writer_b = load_instance(setup, instance.instance_id)
    candidate_a, record_a = _transition(writer_a, "writer-a")
    candidate_b, record_b = _transition(writer_b, "writer-b")
    barrier = threading.Barrier(2)
    results = []

    def writer(candidate, record):
        conn = connect(path)
        barrier.wait()
        try:
            _persist_transition(conn, instance, candidate, record, actor="writer")
            results.append("accepted")
        except ValueError as exc:
            results.append(str(exc))
        finally:
            conn.close()

    threads = [threading.Thread(target=writer, args=item) for item in ((candidate_a, record_a), (candidate_b, record_b))]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
    assert results.count("accepted") == 1
    assert sum("stale instance head" in result for result in results) == 1
    assert verify_durable_graph(setup)[0] == 2


def test_a37_concurrent_different_heads_keep_instance_isolation(tmp_path):
    path = tmp_path / "different-heads.sqlite"
    setup = connect(path)
    first = Instance.create_root("u", State(elements={"root": "first"}))
    second = Instance.create_root("u", State(elements={"root": "second"}))
    save_instance(setup, first)
    save_instance(setup, second)
    candidate_a, record_a = _transition(first, "first-next")
    candidate_b, record_b = _transition(second, "second-next")
    barrier = threading.Barrier(2)
    errors = []

    def writer(instance, candidate, record):
        conn = connect(path)
        barrier.wait()
        try:
            _persist_transition(conn, instance, candidate, record, actor="writer")
        except Exception as exc:
            errors.append(exc)
        finally:
            conn.close()

    threads = [threading.Thread(target=writer, args=item) for item in ((first, candidate_a, record_a), (second, candidate_b, record_b))]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
    assert errors == []
    assert recover_instance(setup, first.instance_id).engine.state.elements["first-next"] == 1
    assert recover_instance(setup, second.instance_id).engine.state.elements["second-next"] == 1


def test_a40_malformed_json_fails_with_storage_corruption_error():
    conn = connect()
    instance = Instance.create_root("u", State(elements={"a": 1}))
    save_instance(conn, instance)
    conn.execute("UPDATE states SET payload=? WHERE state_id=?", ("{malformed", instance.engine.state.state_id))
    with pytest.raises(StorageCorruptionError, match="malformed state JSON"):
        load_instance(conn, instance.instance_id)


def test_a41_missing_current_head_fails_recovery():
    conn = connect()
    instance = Instance.create_root("u", State(elements={"a": 1}))
    save_instance(conn, instance)
    conn.execute("PRAGMA foreign_keys=OFF")
    conn.execute("UPDATE instances SET current_state_id='missing-state' WHERE instance_id=?", (instance.instance_id,))
    with pytest.raises(StorageCorruptionError, match="current head lacks transition provenance"):
        _authorized_recover(conn, instance.instance_id)


def test_durable_graph_rejects_tampered_unheaded_transition_source():
    conn = connect()
    instance = Instance.create_root("u", State(elements={"a": 1}))
    save_instance(conn, instance)

    orphan_source = State(elements={"orphan": 1})
    proposed = orphan_source.with_elements({"orphan": 2})
    candidate = Candidate(orphan_source.state_id, proposed, "unheaded-rejected")
    from gnosis.storage.repositories import save_state, save_candidate, transition_id

    save_state(conn, orphan_source)
    save_candidate(conn, candidate)
    record = TransitionRecord(
        from_state_id=orphan_source.state_id,
        to_state_id=proposed.state_id,
        candidate_id=candidate.candidate_id,
        test_result=TestResult(passed=False, reasons=("rejected",)),
        accepted=False,
        reason="rejected",
        test_rule_id="test-rule",
    )
    tid = transition_id(record)
    conn.execute(
        """INSERT INTO transitions
           (transition_id,instance_id,candidate_id,from_state_id,to_state_id,accepted,reasons,test_rule_id,created_at)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (tid, instance.instance_id, candidate.candidate_id, orphan_source.state_id,
         proposed.state_id, 0, json.dumps(["rejected"]), "test-rule", "now"),
    )
    append_audit(
        conn, actor="u", action="transition.reject", resource=instance.instance_id,
        result="rejected", event_key=f"transition:{tid}", transition_id_value=tid,
    )

    conn.execute("PRAGMA foreign_keys=OFF")
    conn.execute(
        "UPDATE states SET payload=? WHERE state_id=?",
        (json.dumps({"elements": {"orphan": "tampered"}, "version": orphan_source.version},
                    separators=(",", ":")), orphan_source.state_id),
    )
    with pytest.raises(StorageCorruptionError, match="state hash mismatch"):
        verify_durable_graph(conn)


def test_rejected_transition_is_evidence_only_and_cannot_move_head_or_budget():
    conn = connect()
    instance = Instance.create_root("u", State(elements={"root": 0}))
    save_instance(conn, instance)
    original_head = instance.engine.state.state_id
    original_budget = (instance.engine.budget.total, instance.engine.budget.spent)

    proposed = instance.engine.state.with_elements({"rejected": 1})
    candidate = Candidate(instance.engine.state.state_id, proposed, "reject-only")
    rejected = TransitionRecord(
        from_state_id=instance.engine.state.state_id,
        to_state_id=proposed.state_id,
        candidate_id=candidate.candidate_id,
        test_result=TestResult(passed=False, reasons=("rejected",)),
        accepted=False,
        reason="rejected",
        test_rule_id="test-rule",
    )
    _persist_transition(conn, instance, candidate, rejected, actor="u")

    recovered = _authorized_recover(conn, instance.instance_id)
    assert recovered.engine.state.state_id == original_head
    assert (recovered.engine.budget.total, recovered.engine.budget.spent) == original_budget
    assert conn.execute(
        "SELECT count(*) FROM transitions WHERE instance_id=? AND accepted=0",
        (instance.instance_id,),
    ).fetchone()[0] == 1
    assert conn.execute(
        "SELECT 1 FROM states WHERE state_id=?",
        (proposed.state_id,),
    ).fetchone() is not None
    assert verify_durable_graph(conn)[0] == 2


def test_durable_graph_rejects_budget_snapshot_exceeding_total():
    conn = connect()
    instance = Instance.create_root("u", State(elements={"root": 0}))
    save_instance(conn, instance)
    conn.execute(
        "UPDATE instances SET budget_spent=budget_total+1 WHERE instance_id=?",
        (instance.instance_id,),
    )
    with pytest.raises(StorageCorruptionError, match="budget spent exceeds total"):
        verify_durable_graph(conn)


def test_transition_reload_rejects_identity_tampering():
    conn = connect()
    instance = Instance.create_root("u", State(elements={"a": 1}))
    save_instance(conn, instance)
    candidate, record = _transition(instance, "next")
    _persist_transition(conn, instance, candidate, record, actor="u")
    conn.execute(
        "UPDATE transitions SET test_rule_id=? WHERE transition_id=?",
        ("tampered-rule", record.transition_id),
    )
    with pytest.raises(StorageCorruptionError, match="transition identity mismatch"):
        from gnosis.storage.repositories import load_transition_records
        load_transition_records(conn, instance.instance_id)


def test_transition_reload_identity_is_independent_of_created_at():
    conn = connect()
    instance = Instance.create_root("u", State(elements={"a": 1}))
    save_instance(conn, instance)
    candidate, record = _transition(instance, "next")
    _persist_transition(conn, instance, candidate, record, actor="u")
    conn.execute(
        "UPDATE transitions SET created_at=? WHERE transition_id=?",
        ("2099-01-01T00:00:00+00:00", record.transition_id),
    )
    loaded = __import__("gnosis.storage.repositories", fromlist=["load_transition_records"]).load_transition_records(
        conn, instance.instance_id
    )
    assert loaded[0].transition_id == record.transition_id
