"""Real SQLite commit-path rollback proof using the production trust boundary."""
import pytest

from test_production_trust_context import _make_real_commit_case


def _inject_persistence_failure(monkeypatch, failure_at):
    from gnosis.reflection import execution_adapter as adapter_module

    persist = adapter_module._persist_transition_in_transaction

    def fail_at_requested_point(conn, instance, candidate, record, *, actor, failure_at=None):
        return persist(
            conn, instance, candidate, record, actor=actor, failure_at=failure_at_requested_point.point
        )

    fail_at_requested_point.point = failure_at
    monkeypatch.setattr(adapter_module, "_persist_transition_in_transaction", fail_at_requested_point)


def test_real_commit_rolls_back_after_persistence_failure(sqlite_conn, monkeypatch):
    from gnosis.storage import load_instance

    adapter, instance, candidate, record, request, signed, context, _ = (
        _make_real_commit_case(sqlite_conn, nonce="failure-injection-after-audit")
    )
    before_state = load_instance(sqlite_conn, instance.instance_id).engine.state.state_id
    _inject_persistence_failure(monkeypatch, "after_audit")

    with pytest.raises(RuntimeError, match="after_audit"):
        adapter.commit(
            sqlite_conn, instance, candidate, record, request,
            actor="integration-owner",
            production_authorization=signed,
            trust_context=context,
        )

    assert sqlite_conn.execute(
        "SELECT 1 FROM audit_events WHERE event_id=?",
        (f"execution-authorization-nonce:{signed.nonce}",),
    ).fetchone() is None
    assert sqlite_conn.execute(
        "SELECT 1 FROM transitions WHERE transition_id=?",
        (record.transition_id,),
    ).fetchone() is None
    assert load_instance(sqlite_conn, instance.instance_id).engine.state.state_id == before_state


def test_real_commit_failure_injection_is_not_silent(sqlite_conn, monkeypatch):
    adapter, instance, candidate, record, request, signed, context, _ = (
        _make_real_commit_case(sqlite_conn, nonce="failure-injection-after-transition")
    )
    _inject_persistence_failure(monkeypatch, "after_transition")

    with pytest.raises(RuntimeError, match="after_transition"):
        adapter.commit(
            sqlite_conn, instance, candidate, record, request,
            actor="integration-owner",
            production_authorization=signed,
            trust_context=context,
        )
