"""Real SQLite commit-path rollback proof using the adapter's failure injection."""
import pytest


def _event(conn, authorization_id):
    return conn.execute("SELECT event_hash FROM audit_events WHERE event_id=?", (f"execution-authorization:{authorization_id}",)).fetchone()


def test_real_commit_rolls_back_after_persistence_failure(real_commit_fixture):
    conn = real_commit_fixture.conn
    instance = real_commit_fixture.instance
    candidate = real_commit_fixture.candidate
    record = real_commit_fixture.record
    request = real_commit_fixture.request
    request.failure_injection = "after_audit"
    before_head = instance.engine.state.state_id
    with pytest.raises(RuntimeError, match="after_audit"):
        real_commit_fixture.adapter.commit(conn, instance, candidate, record, request, actor="trusted-owner", failure_at="after_audit")
    assert _event(conn, request.authorization.approval_id) is None
    assert conn.execute("SELECT 1 FROM transitions WHERE transition_id=?", (record.transition_id,)).fetchone() is None
    assert conn.execute("SELECT 1 FROM candidates WHERE candidate_id=?", (record.candidate_id,)).fetchone() is None
    assert instance.engine.state.state_id == before_head


def test_real_commit_failure_injection_is_not_silent(real_commit_fixture):
    conn = real_commit_fixture.conn
    instance = real_commit_fixture.instance
    candidate = real_commit_fixture.candidate
    record = real_commit_fixture.record
    request = real_commit_fixture.request
    request.failure_injection = "after_transition"
    with pytest.raises(RuntimeError, match="after_transition"):
        real_commit_fixture.adapter.commit(conn, instance, candidate, record, request, actor="trusted-owner", failure_at="after_commit")
