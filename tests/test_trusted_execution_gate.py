import pytest
from gnosis.reflection.authority import ExecutionAuthorization, ExecutionCommitRequest, ExecutionIntentSnapshot
from gnosis.reflection.trusted_execution_gate import require_trusted_execution
from gnosis.reflection.authorization_validity import AuthorizationValidity


def test_gate_rejects_revoked_before_consumption(sqlite_conn, provenance):
    auth=ExecutionAuthorization(request_provenance=provenance.provenance_id,owner_approved=True,evolution_identity=provenance.evolution_identity,approval_id="auth-1")
    validity=AuthorizationValidity("auth-1","policy-1","ev-1",revoked=True)
    req=ExecutionCommitRequest(auth,ExecutionIntentSnapshot.from_provenance(provenance),provenance.provenance_id,provenance.evolution_identity,provenance,validity)
    with pytest.raises(PermissionError,match="revoked"):
        require_trusted_execution(req,conn=sqlite_conn,actor="trusted-owner")


def test_gate_rejects_identity_mismatch_before_consumption(sqlite_conn, provenance):
    auth=ExecutionAuthorization(request_provenance=provenance.provenance_id,owner_approved=True,evolution_identity=provenance.evolution_identity,approval_id="auth-1")
    validity=AuthorizationValidity("other-auth","policy-1","ev-1")
    req=ExecutionCommitRequest(auth,ExecutionIntentSnapshot.from_provenance(provenance),provenance.provenance_id,provenance.evolution_identity,provenance,validity)
    with pytest.raises(PermissionError,match="identity"):
        require_trusted_execution(req,conn=sqlite_conn,actor="trusted-owner")
