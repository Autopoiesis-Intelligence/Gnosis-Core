import pytest
from dataclasses import FrozenInstanceError
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.authority import ExecutionAuthorization, ExecutionCommitRequest, ExecutionIntentSnapshot
from gnosis.reflection.trusted_execution_gate import require_trusted_execution, TrustedExecutionContext


def make_request(provenance, validity):
    auth=ExecutionAuthorization(request_provenance=provenance.provenance_id,owner_approved=True,evolution_identity=provenance.evolution_identity,approval_id=validity.authorization_id)
    return ExecutionCommitRequest(auth,ExecutionIntentSnapshot.from_provenance(provenance),provenance.provenance_id,provenance.evolution_identity,provenance,validity)


def test_validity_is_immutable(provenance):
    v=AuthorizationValidity("auth-t","policy-1","ev-1")
    with pytest.raises(FrozenInstanceError):
        v.authorization_id="forged"


def test_tampered_policy_is_rejected_before_consumption(sqlite_conn, provenance):
    v=AuthorizationValidity("auth-t","policy-forged","ev-1")
    req=make_request(provenance,v)
    with pytest.raises(PermissionError):
        require_trusted_execution(req,conn=sqlite_conn,actor="trusted-owner",trusted_context=TrustedExecutionContext(policy_version="policy-1"))
    row=sqlite_conn.execute("SELECT event_hash FROM audit_events WHERE event_id=?",("execution-authorization:auth-t",)).fetchone()
    assert row is None


def test_missing_trusted_context_fails_closed(sqlite_conn, provenance):
    v=AuthorizationValidity("auth-missing","policy-1","ev-1")
    req=make_request(provenance,v)
    with pytest.raises(PermissionError, match="trusted execution context is required"):
        require_trusted_execution(req,conn=sqlite_conn,actor="trusted-owner")

