"""Real SQLite commit-path rollback proof using the adapter failure-injection seam."""
import pytest


def _event(conn, authorization_id):
    return conn.execute(
        "SELECT event_hash FROM audit_events WHERE event_id=?",
        (f"execution-authorization:{authorization_id}",),
    ).fetchone()


def test_real_commit_rolls_back_after_persistence_failure(real_commit_fixture):
    conn, instance, candidate, record, request, adapter = real_commit_fixture
    before_head = instance.engine.state.state_id
    with pytest.raises(RuntimeError, match="after_audit"):
        adapter.commit(
            conn, instance, candidate, record, request,
            actor="trusted-owner", failure_injection="after_audit",
        )
    assert _event(conn, request.authorization.approval_id) is None
    assert conn.execute(
        "SELECT 1 FROM transitions WHERE transition_id=?", (record.transition_id,)
    ).fetchone() is None
    assert conn.execute(
        "SELECT 1 FROM candidates WHERE candidate_id=?", (record.candidate_id,)
    ).fetchone() is None
    assert instance.engine.state.state_id == before_head
    assert conn.execute("SELECT current_state_id FROM instances WHERE instance_id=?",
                        (instance.instance_id,)).fetchone()[0] == candidate.parent_state_id


def test_real_commit_failure_injection_is_not_silent(real_commit_fixture):
    conn, instance, candidate, record, request, adapter = real_commit_fixture
    with pytest.raises(RuntimeError, match="after_transition"):
        adapter.commit(
            conn, instance, candidate, record, request,
            actor="trusted-owner", failure_injection="after_transition",
        )
    assert _event(conn, request.authorization.approval_id) is None
    assert conn.execute(
        "SELECT 1 FROM transitions WHERE transition_id=?", (record.transition_id,)
    ).fetchone() is None
