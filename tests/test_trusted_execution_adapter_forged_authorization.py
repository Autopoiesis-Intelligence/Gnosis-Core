"""End-to-end regression: forged authorization must not persist a Core transition.

This test is intentionally red until the trusted issuer provenance boundary exists.
It asserts rejection at the trust boundary, no persisted proposed state, and no
authorization-consumption audit event after the transaction exits.
"""
import pytest

from gnosis.storage import StorageCorruptionError, load_state


def test_forged_authorization_cannot_commit_or_persist(real_commit_fixture):
    fixture = real_commit_fixture
    request = fixture.request
    conn = fixture.conn
    proposed_state_id = fixture.candidate.proposed_state.state_id
    authorization_id = request.authorization_validity.authorization_id

    # The fixture has persisted the root instance, not this proposed state.
    with pytest.raises(StorageCorruptionError, match="state not found"):
        load_state(conn, proposed_state_id)

    with pytest.raises(PermissionError, match="issuer|trusted|provenance"):
        fixture.adapter.commit(
            conn,
            fixture.instance,
            fixture.candidate,
            fixture.record,
            request,
            actor="adversarial-test",
        )

    # Re-open the relevant facts from durable storage, not the in-memory instance.
    with pytest.raises(StorageCorruptionError, match="state not found"):
        load_state(conn, proposed_state_id)

    row = conn.execute(
        "SELECT event_hash FROM audit_events WHERE event_id = ?",
        (f"execution-authorization:{authorization_id}",),
    ).fetchone()
    assert row is None
