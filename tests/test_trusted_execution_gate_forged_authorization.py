"""Regression test: caller-constructed authorization must not cross the trusted gate.

This test is intentionally expected to fail on the current candidate until the
issuer-provenance boundary is implemented. It must not be weakened to match the
current unsafe behavior.
"""
import pytest

from gnosis.reflection.trusted_execution_gate import require_trusted_execution


def test_caller_constructed_authorization_is_rejected_before_consumption(real_commit_fixture):
    fixture = real_commit_fixture
    request = fixture.request
    conn = fixture.conn
    authorization_id = request.authorization_validity.authorization_id

    with pytest.raises(PermissionError):
        require_trusted_execution(
            request,
            conn=conn,
            actor="adversarial-test",
        )

    row = conn.execute(
        "SELECT event_hash FROM audit_events WHERE event_id = ?",
        (f"execution-authorization:{authorization_id}",),
    ).fetchone()
    assert row is None
