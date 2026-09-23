import sqlite3
import pytest

from gnosis.reflection.test_issuer import (
    TestAuthorizationIssuer,
    consume_test_authorization,
    initialize_test_authorization_store,
    persist_test_authorization,
    revoke_test_authorization,
)


def _issued():
    issuer = TestAuthorizationIssuer(secret=b"e5.20-test-secret")
    auth = issuer.issue(
        request_provenance="provenance:p1",
        evolution_identity="evolution:e1",
        parent_state_digest="parent-1",
        policy_version="policy:v1",
        scope=("test:execute",),
        expires_at=100,
    )
    return issuer, auth


def test_e520_issuer_binds_exact_context_and_verifies():
    issuer, auth = _issued()
    assert issuer.verify(auth)
    assert auth.request_provenance == "provenance:p1"
    assert auth.evolution_identity == "evolution:e1"
    assert auth.parent_state_digest == "parent-1"


def test_e520_tampered_payload_fails_verification():
    issuer, auth = _issued()
    tampered = type(auth)(**{**auth.__dict__, "evolution_identity": "evolution:other"})
    assert issuer.verify(tampered) is False


def test_e520_persistence_consumption_and_replay_rejection():
    issuer, auth = _issued()
    conn = sqlite3.connect(":memory:")
    initialize_test_authorization_store(conn)
    persist_test_authorization(conn, auth)
    consume_test_authorization(
        conn, issuer, auth, now=50,
        request_provenance="provenance:p1",
        evolution_identity="evolution:e1",
        parent_state_digest="parent-1",
        policy_version="policy:v1",
    )
    with pytest.raises(PermissionError, match="already consumed"):
        consume_test_authorization(
            conn, issuer, auth, now=50,
            request_provenance="provenance:p1",
            evolution_identity="evolution:e1",
            parent_state_digest="parent-1",
            policy_version="policy:v1",
        )


def test_e520_expiry_and_revocation_fail_closed():
    issuer, auth = _issued()
    conn = sqlite3.connect(":memory:")
    initialize_test_authorization_store(conn)
    persist_test_authorization(conn, auth)
    with pytest.raises(PermissionError, match="expired"):
        consume_test_authorization(
            conn, issuer, auth, now=101,
            request_provenance="provenance:p1",
            evolution_identity="evolution:e1",
            parent_state_digest="parent-1",
            policy_version="policy:v1",
        )
    revoke_test_authorization(conn, auth.authorization_id)
    with pytest.raises(PermissionError, match="revoked"):
        consume_test_authorization(
            conn, issuer, auth, now=50,
            request_provenance="provenance:p1",
            evolution_identity="evolution:e1",
            parent_state_digest="parent-1",
            policy_version="policy:v1",
        )


def test_e520_bridge_preserves_exact_execution_boundary():
    from gnosis.reflection.authority import require_execution_authorization
    from gnosis.reflection.test_issuer import to_execution_authorization_for_test

    issuer, auth = _issued()
    execution_auth = to_execution_authorization_for_test(issuer, auth)
    require_execution_authorization(
        execution_auth,
        request_provenance="provenance:p1",
        evolution_identity="evolution:e1",
    )
    with pytest.raises(PermissionError):
        require_execution_authorization(
            execution_auth,
            request_provenance="provenance:other",
            evolution_identity="evolution:e1",
        )
