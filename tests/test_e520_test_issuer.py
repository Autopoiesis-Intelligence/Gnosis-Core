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


def test_e522_issuer_binds_execution_intent_snapshot_exactly():
    from gnosis.reflection.authority import ExecutionIntentSnapshot, require_execution_intent_snapshot
    from gnosis.reflection.test_issuer import issue_for_provenance_for_test, to_execution_authorization_for_test
    from tests.test_authority_boundary import _snapshot_provenance

    provenance = _snapshot_provenance()
    issuer = TestAuthorizationIssuer(secret=b"e5.22-test-secret")
    auth = issue_for_provenance_for_test(
        issuer, provenance, policy_version="policy:v1", expires_at=100
    )
    execution_auth = to_execution_authorization_for_test(issuer, auth)
    snapshot = ExecutionIntentSnapshot.from_provenance(provenance)
    require_execution_intent_snapshot(snapshot, provenance)
    assert execution_auth.evolution_identity == snapshot.evolution_identity
    assert execution_auth.request_provenance == snapshot.provenance_id

    changed = type(provenance)(**{**provenance.__dict__, "parent_state_digest": "stale-parent"})
    with pytest.raises(PermissionError):
        require_execution_intent_snapshot(snapshot, changed)
    with pytest.raises(PermissionError):
        to_execution_authorization_for_test(
            issuer,
            type(auth)(**{**auth.__dict__, "evolution_identity": "evolution:other"}),
        )


def test_e523_restart_persistence_does_not_resurrect_consumed_or_revoked_authority(tmp_path):
    db = tmp_path / "auth.sqlite3"
    issuer = TestAuthorizationIssuer(secret=b"e5.23-test-secret")
    auth1 = issuer.issue(request_provenance="p1", evolution_identity="e1", parent_state_digest="s1", policy_version="v1", scope=("test:execute",), expires_at=100)
    conn = sqlite3.connect(db)
    initialize_test_authorization_store(conn)
    persist_test_authorization(conn, auth1)
    consume_test_authorization(conn, issuer, auth1, now=50, request_provenance="p1", evolution_identity="e1", parent_state_digest="s1", policy_version="v1")
    conn.close()
    conn = sqlite3.connect(db)
    with pytest.raises(PermissionError, match="already consumed"):
        consume_test_authorization(conn, issuer, auth1, now=50, request_provenance="p1", evolution_identity="e1", parent_state_digest="s1", policy_version="v1")

    auth2 = issuer.issue(request_provenance="p2", evolution_identity="e2", parent_state_digest="s2", policy_version="v1", scope=("test:execute",), expires_at=100)
    persist_test_authorization(conn, auth2)
    revoke_test_authorization(conn, auth2.authorization_id)
    conn.close()
    conn = sqlite3.connect(db)
    with pytest.raises(PermissionError, match="revoked"):
        consume_test_authorization(conn, issuer, auth2, now=50, request_provenance="p2", evolution_identity="e2", parent_state_digest="s2", policy_version="v1")
