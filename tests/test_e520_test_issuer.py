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
    from test_authority_boundary import _snapshot_provenance

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

def test_e524_sqlite_payload_tamper_fails_closed(tmp_path):
    db = tmp_path / "tamper.sqlite3"
    issuer, auth = _issued()
    conn = sqlite3.connect(db)
    initialize_test_authorization_store(conn)
    persist_test_authorization(conn, auth)
    conn.execute(
        "UPDATE test_authorizations SET evolution_identity = ? WHERE authorization_id = ?",
        ("evolution:tampered", auth.authorization_id),
    )
    conn.commit()
    with pytest.raises(PermissionError, match="registry integrity|registry payload mismatch"):
        consume_test_authorization(
            conn, issuer, auth, now=50,
            request_provenance="provenance:p1",
            evolution_identity="evolution:e1",
            parent_state_digest="parent-1",
            policy_version="policy:v1",
        )


def test_e524_sqlite_state_tamper_cannot_unconsume(tmp_path):
    db = tmp_path / "state-tamper.sqlite3"
    issuer, auth = _issued()
    conn = sqlite3.connect(db)
    initialize_test_authorization_store(conn)
    persist_test_authorization(conn, auth)
    consume_test_authorization(
        conn, issuer, auth, now=50,
        request_provenance="provenance:p1",
        evolution_identity="evolution:e1",
        parent_state_digest="parent-1",
        policy_version="policy:v1",
    )
    conn.execute(
        "UPDATE test_authorizations SET consumed = 0 WHERE authorization_id = ?",
        (auth.authorization_id,),
    )
    conn.commit()
    with pytest.raises(PermissionError, match="registry integrity"):
        consume_test_authorization(
            conn, issuer, auth, now=50,
            request_provenance="provenance:p1",
            evolution_identity="evolution:e1",
            parent_state_digest="parent-1",
            policy_version="policy:v1",
        )

def test_e525_persistence_cannot_mint_new_authority(tmp_path):
    db = tmp_path / "registry-only.sqlite3"
    issuer = TestAuthorizationIssuer(secret=b"e5.25-test-secret")
    forged = issuer.issue(
        request_provenance="p1", evolution_identity="e1",
        parent_state_digest="s1", policy_version="v1",
        scope=("test:execute",), expires_at=100,
    )
    # Simulate a database-only fabricated record by replacing the signed payload.
    fabricated = type(forged)(**{
        **forged.__dict__,
        "request_provenance": "p2",
        "authorization_id": "auth:database-only",
    })
    conn = sqlite3.connect(db)
    initialize_test_authorization_store(conn)
    persist_test_authorization(conn, fabricated)
    with pytest.raises(PermissionError, match="invalid test authorization"):
        consume_test_authorization(
            conn, issuer, fabricated, now=50,
            request_provenance="p2", evolution_identity="e1",
            parent_state_digest="s1", policy_version="v1",
        )


def test_e525_registry_has_no_issuance_operation():
    from gnosis.reflection import test_issuer
    assert not hasattr(test_issuer, "issue_test_authorization")

def test_e526_expiry_is_monotonic_and_never_extends_authority():
    from gnosis.reflection.test_issuer import expire_test_authorization
    issuer, auth = _issued()
    conn = sqlite3.connect(":memory:")
    initialize_test_authorization_store(conn)
    persist_test_authorization(conn, auth)
    expire_test_authorization(conn, auth, now=101)
    with pytest.raises(PermissionError, match="expired"):
        consume_test_authorization(
            conn, issuer, auth, now=101,
            request_provenance="provenance:p1",
            evolution_identity="evolution:e1",
            parent_state_digest="parent-1",
            policy_version="policy:v1",
        )
    with pytest.raises(ValueError, match="not expired"):
        expire_test_authorization(conn, auth, now=100)


def test_e526_lifecycle_cannot_reverse_consumed_or_revoked_state():
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

def test_e527_lifecycle_reasons_are_distinct_and_terminal():
    from gnosis.reflection.test_issuer import expire_test_authorization
    issuer, auth = _issued()
    conn = sqlite3.connect(":memory:")
    initialize_test_authorization_store(conn)
    persist_test_authorization(conn, auth)
    expire_test_authorization(conn, auth, now=101)
    state = conn.execute(
        "SELECT lifecycle_state, consumed, revoked FROM test_authorizations WHERE authorization_id = ?",
        (auth.authorization_id,),
    ).fetchone()
    assert state == ("expired", 0, 0)
    with pytest.raises(PermissionError, match="expired"):
        consume_test_authorization(
            conn, issuer, auth, now=101,
            request_provenance="provenance:p1",
            evolution_identity="evolution:e1",
            parent_state_digest="parent-1",
            policy_version="policy:v1",
        )

    issuer2, auth2 = _issued()
    persist_test_authorization(conn, auth2)
    revoke_test_authorization(conn, auth2.authorization_id)
    state2 = conn.execute(
        "SELECT lifecycle_state, consumed, revoked FROM test_authorizations WHERE authorization_id = ?",
        (auth2.authorization_id,),
    ).fetchone()
    assert state2 == ("revoked", 0, 1)


def test_e527_consumed_reason_is_distinct_from_revoked():
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
    state = conn.execute(
        "SELECT lifecycle_state, consumed, revoked FROM test_authorizations WHERE authorization_id = ?",
        (auth.authorization_id,),
    ).fetchone()
    assert state == ("consumed", 1, 0)


def test_e760_test_authority_lifecycle_reaches_real_sqlite_execution() -> None:
    """Bridge persisted test authority into the existing trusted execution boundary."""
    from gnosis.core import Candidate, State
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.instances.instance import Instance
    from gnosis.reflection.authority import (
        ExecutionCommitRequest,
        ExecutionIntentSnapshot,
    )
    from gnosis.reflection.authorization_validity import AuthorizationValidity
    from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter
    from gnosis.reflection.test_issuer import (
        issue_for_provenance_for_test,
        to_execution_authorization_for_test,
    )
    from gnosis.storage import connect, load_instance, save_instance

    conn = connect()
    initialize_test_authorization_store(conn)

    instance = Instance.create_root("e760-test", State(elements={"a": 1}))
    save_instance(conn, instance)
    parent_state_id = instance.engine.state.state_id
    proposed = instance.engine.state.with_elements({"a": 2})
    candidate = Candidate(parent_state_id, proposed, "e760-vertical")
    record = instance.engine.step(candidate)

    observations = {"candidate_id": candidate.candidate_id, "result": "ok"}
    provenance = build_provenance(
        candidate_id=candidate.candidate_id,
        parent_state_id=parent_state_id,
        parent_state_digest=parent_state_id,
        proposed_state_digest=proposed.state_id,
        observations=observations,
        proposed_state_content_id=proposed.content_id,
        candidate_binding_digest=candidate.binding_digest(parent_state_id),
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="UNCHANGED",
        invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )

    issuer = TestAuthorizationIssuer(secret=b"e7.60-vertical-test-secret")
    authorization = issue_for_provenance_for_test(
        issuer,
        provenance,
        policy_version="policy:v1",
        expires_at=100,
    )
    persist_test_authorization(conn, authorization)
    consume_test_authorization(
        conn,
        issuer,
        authorization,
        now=50,
        request_provenance=provenance.provenance_id,
        evolution_identity=provenance.evolution_identity,
        parent_state_digest=provenance.parent_state_digest,
        policy_version="policy:v1",
    )

    execution_auth = to_execution_authorization_for_test(issuer, authorization)
    snapshot = ExecutionIntentSnapshot.from_provenance(provenance)
    request = ExecutionCommitRequest(
        authorization=execution_auth,
        intent_snapshot=snapshot,
        request_provenance=provenance.provenance_id,
        evolution_identity=provenance.evolution_identity,
        provenance=provenance,
        authorization_validity=AuthorizationValidity(
            authorization.authorization_id,
            "policy:v1",
            provenance.evidence_digest,
        ),
    )

    result = SQLiteExecutionCommitAdapter().commit(
        conn,
        instance,
        candidate,
        record,
        request,
        actor="e760-test",
    )

    assert result.resulting_state_id == proposed.state_id
    assert result.receipt.matches_request(request)
    assert load_instance(conn, instance.instance_id).engine.state.state_id == proposed.state_id
    lifecycle = conn.execute(
        "SELECT consumed, lifecycle_state FROM test_authorizations WHERE authorization_id = ?",
        (authorization.authorization_id,),
    ).fetchone()
    assert tuple(lifecycle) == (1, "consumed")

    with pytest.raises(PermissionError, match="already consumed"):
        consume_test_authorization(
            conn,
            issuer,
            authorization,
            now=50,
            request_provenance=provenance.provenance_id,
            evolution_identity=provenance.evolution_identity,
            parent_state_digest=provenance.parent_state_digest,
            policy_version="policy:v1",
        )
    conn.close()
