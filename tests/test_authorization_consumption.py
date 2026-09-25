import pytest
from gnosis.reflection.authorization_consumption import consume_authorization


def test_consumption_is_one_time(sqlite_conn):
    first=consume_authorization(sqlite_conn,"auth-1",request_provenance="p1",evolution_identity="e1",policy_version="policy-1",actor="trusted-owner")
    assert first.consumed is True
    with pytest.raises(PermissionError,match="already consumed"):
        consume_authorization(sqlite_conn,"auth-1",request_provenance="p1",evolution_identity="e1",policy_version="policy-1",actor="trusted-owner")


def test_missing_identity_fails_closed(sqlite_conn):
    with pytest.raises(PermissionError):
        consume_authorization(sqlite_conn,"",request_provenance="p1",evolution_identity="e1",policy_version="policy-1",actor="trusted-owner")
