"""End-to-end regression: forged authorization must not persist a Core transition.

The test records whether the adapter rejects the request and inspects durable
state/audit after the call. It fails closed as a regression test, while its
failure message preserves evidence if the forged request was committed.
"""
from gnosis.storage import StorageCorruptionError, load_state


def test_forged_authorization_cannot_commit_or_persist(real_commit_fixture):
    fixture = real_commit_fixture
    request = fixture.request
    conn = fixture.conn
    proposed_state_id = fixture.candidate.proposed_state.state_id
    authorization_id = request.authorization_validity.authorization_id

    with __import__("pytest").raises(StorageCorruptionError, match="state not found"):
        load_state(conn, proposed_state_id)

    rejected = False
    result = None
    try:
        result = fixture.adapter.commit(
            conn,
            fixture.instance,
            fixture.candidate,
            fixture.record,
            request,
            actor="adversarial-test",
        )
    except PermissionError:
        rejected = True

    try:
        persisted_state = load_state(conn, proposed_state_id)
        proposed_state_persisted = persisted_state.state_id == proposed_state_id
    except StorageCorruptionError:
        proposed_state_persisted = False

    row = conn.execute(
        "SELECT event_hash FROM audit_events WHERE event_id = ?",
        (f"execution-authorization:{authorization_id}",),
    ).fetchone()
    audit_event_present = row is not None

    assert rejected, (
        "FORGED AUTHORIZATION ACCEPTED at SQLiteExecutionCommitAdapter; "
        f"proposed_state_persisted={proposed_state_persisted}; "
        f"authorization_consumption_audit_present={audit_event_present}; "
        f"result_returned={result is not None}"
    )
    assert not proposed_state_persisted, "rejected forged request persisted proposed state"
    assert not audit_event_present, "rejected forged request left authorization-consumption audit event"
