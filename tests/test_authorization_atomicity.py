import pytest
from gnosis.reflection.authorization_consumption import consume_authorization_in_transaction
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.authority import ExecutionAuthorization, ExecutionCommitRequest, ExecutionIntentSnapshot
from gnosis.reflection.trusted_execution_gate import require_trusted_execution


def test_consumption_rolls_back_with_outer_transaction(sqlite_conn):
    from gnosis.storage.database import transaction
    with pytest.raises(RuntimeError):
        with transaction(sqlite_conn):
            consume_authorization_in_transaction(sqlite_conn,"auth-atomic",request_provenance="p1",evolution_identity="e1",policy_version="policy-1",actor="trusted-owner")
            raise RuntimeError("injected post-consumption failure")
    row=sqlite_conn.execute("SELECT event_hash FROM audit_events WHERE event_id=?",("execution-authorization:auth-atomic",)).fetchone()
    assert row is None


def test_validity_is_immutable_binding():
    v=AuthorizationValidity("auth-1","policy-1","ev-1")
    with pytest.raises(Exception):
        v.authorization_id="forged"


def test_trusted_execution_consumption_rolls_back_with_outer_transaction(sqlite_conn):
    auth = ExecutionAuthorization(
        approval_id="auth-gate-atomic",
        owner_approved=True,
        request_provenance="p1",
        evolution_identity="e1",
    )
    from tests.test_authority_boundary import _snapshot_provenance
    provenance = _snapshot_provenance()
    auth = ExecutionAuthorization(
        approval_id="auth-gate-atomic",
        owner_approved=True,
        request_provenance=provenance.provenance_id,
        evolution_identity=provenance.evolution_identity,
    )
    validity = AuthorizationValidity("auth-gate-atomic", "policy-1", provenance.evidence_digest)
    request = ExecutionCommitRequest(
        authorization=auth,
        intent_snapshot=ExecutionIntentSnapshot.from_provenance(provenance),
        request_provenance=provenance.provenance_id,
        evolution_identity=provenance.evolution_identity,
        provenance=provenance,
        authorization_validity=validity,
    )
    with pytest.raises(RuntimeError):
        from gnosis.storage.database import transaction
        with transaction(sqlite_conn):
            require_trusted_execution(request, conn=sqlite_conn, actor="trusted-owner")
            raise RuntimeError("injected post-gate failure")
    row = sqlite_conn.execute("SELECT event_hash FROM audit_events WHERE event_id=?", ("execution-authorization:auth-gate-atomic",)).fetchone()
    assert row is None
