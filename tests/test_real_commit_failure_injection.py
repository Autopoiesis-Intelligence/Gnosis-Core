"""Real SQLite commit-path rollback proof with test-local failure injection."""
import pytest
import gnosis.reflection.execution_adapter as execution_adapter


def _event(conn, authorization_id):
    return conn.execute("SELECT event_hash FROM audit_events WHERE event_id=?", (f"execution-authorization:{authorization_id}",)).fetchone()


def test_real_commit_rolls_back_after_persistence_failure(real_commit_fixture, monkeypatch):
    conn, instance, candidate, record, request = real_commit_fixture
    before_head = instance.engine.state.state_id
    original = execution_adapter._persist_transition_in_transaction
    def fail_after_audit(*args, **kwargs):
        return original(*args, **{**kwargs, "failure_at": "after_audit"})
    monkeypatch.setattr(execution_adapter, "_persist_transition_in_transaction", fail_after_audit)
    with pytest.raises(RuntimeError, match="after_audit"):
        real_commit_fixture.adapter.commit(conn, instance, candidate, record, request, actor="trusted-owner")
    assert _event(conn, request.authorization.approval_id) is None
    assert conn.execute("SELECT 1 FROM transitions WHERE transition_id=?", (record.transition_id,)).fetchone() is None
    assert conn.execute("SELECT 1 FROM candidates WHERE candidate_id=?", (record.candidate_id,)).fetchone() is None
    assert instance.engine.state.state_id == before_head


def test_real_commit_failure_injection_is_not_silent(real_commit_fixture, monkeypatch):
    conn, instance, candidate, record, request = real_commit_fixture
    original = execution_adapter._persist_transition_in_transaction
    def fail_after_transition(*args, **kwargs):
        return original(*args, **{**kwargs, "failure_at": "after_transition"})
    monkeypatch.setattr(execution_adapter, "_persist_transition_in_transaction", fail_after_transition)
    with pytest.raises(RuntimeError, match="after_transition"):
        real_commit_fixture.adapter.commit(conn, instance, candidate, record, request, actor="trusted-owner")
