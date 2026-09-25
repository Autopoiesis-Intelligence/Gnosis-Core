"""R2 proof cases for authorization consumption + persisted commit atomicity."""
import pytest
from gnosis.reflection.authorization_consumption import consume_authorization_in_transaction


def _event(conn, authorization_id):
    return conn.execute("SELECT event_hash FROM audit_events WHERE event_id=?", (f"execution-authorization:{authorization_id}",)).fetchone()


def test_post_consumption_failure_rolls_back_authorization(sqlite_conn):
    from gnosis.storage.database import transaction
    with pytest.raises(RuntimeError):
        with transaction(sqlite_conn):
            consume_authorization_in_transaction(sqlite_conn,"atomic-proof",request_provenance="p",evolution_identity="e",policy_version="policy-1",actor="trusted-owner")
            raise RuntimeError("injected mutation failure")
    assert _event(sqlite_conn,"atomic-proof") is None


def test_replay_is_rejected_without_second_consumption(sqlite_conn):
    from gnosis.storage.database import transaction
    with transaction(sqlite_conn):
        consume_authorization_in_transaction(sqlite_conn,"replay-proof",request_provenance="p",evolution_identity="e",policy_version="policy-1",actor="trusted-owner")
    with pytest.raises(PermissionError, match="already consumed"):
        with transaction(sqlite_conn):
            consume_authorization_in_transaction(sqlite_conn,"replay-proof",request_provenance="p",evolution_identity="e",policy_version="policy-1",actor="trusted-owner")
    assert _event(sqlite_conn,"replay-proof") is not None
