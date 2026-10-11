"""Real SQLite commit-path rollback proof using the production trust boundary.

The focused production-trust tests own the shared authorized-commit fixture. These
checks exercise the adapter's explicit failure-injection points with that same
signed authorization and trusted context.
"""
import pytest

from test_production_trust_context import _make_real_commit_case


def test_real_commit_rolls_back_after_persistence_failure(sqlite_conn):
    from gnosis.storage import load_instance

    adapter, instance, candidate, record, request, signed, context, _ = (
        _make_real_commit_case(sqlite_conn, nonce="failure-injection-after-audit")
    )
    request.failure_injection = "after_audit"
    before_state = load_instance(sqlite_conn, instance.instance_id).engine.state.state_id

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


def test_real_commit_failure_injection_is_not_silent(sqlite_conn):
    adapter, instance, candidate, record, request, signed, context, _ = (
        _make_real_commit_case(sqlite_conn, nonce="failure-injection-after-transition")
    )
    request.failure_injection = "after_transition"

    with pytest.raises(RuntimeError, match="after_transition"):
        adapter.commit(
            sqlite_conn, instance, candidate, record, request,
            actor="integration-owner",
            production_authorization=signed,
            trust_context=context,
        )
