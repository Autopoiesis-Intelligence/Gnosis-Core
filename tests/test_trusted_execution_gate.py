import pytest
from gnosis.reflection.authority import ExecutionAuthorization, ExecutionCommitRequest, ExecutionIntentSnapshot
from gnosis.reflection.trusted_execution_gate import require_trusted_execution
from gnosis.reflection.authorization_validity import AuthorizationValidity


def test_gate_rejects_revoked_before_consumption(sqlite_conn, provenance):
    auth=ExecutionAuthorization(request_provenance=provenance.provenance_id,owner_approved=True,evolution_identity=provenance.evolution_identity,approval_id="auth-1",policy_version="policy-1")
    validity=AuthorizationValidity("auth-1","policy-1","ev-1",revoked=True)
    req=ExecutionCommitRequest(auth,ExecutionIntentSnapshot.from_provenance(provenance),provenance.provenance_id,provenance.evolution_identity,provenance,validity)
    with pytest.raises(PermissionError,match="revoked"):
        require_trusted_execution(req,conn=sqlite_conn,actor="trusted-owner")


def test_gate_rejects_identity_mismatch_before_consumption(sqlite_conn, provenance):
    auth=ExecutionAuthorization(request_provenance=provenance.provenance_id,owner_approved=True,evolution_identity=provenance.evolution_identity,approval_id="auth-1",policy_version="policy-1")
    validity=AuthorizationValidity("other-auth","policy-1","ev-1")
    req=ExecutionCommitRequest(auth,ExecutionIntentSnapshot.from_provenance(provenance),provenance.provenance_id,provenance.evolution_identity,provenance,validity)
    with pytest.raises(PermissionError,match="identity"):
        require_trusted_execution(req,conn=sqlite_conn,actor="trusted-owner")


def test_gate_consumes_only_issuer_attested_authorization(sqlite_conn, provenance):
    from gnosis.reflection.authority import OwnerApproval
    from gnosis.reflection.trusted_issuer import TrustedIssuerInput, TrustedOwnerIssuer
    approval = OwnerApproval("auth-attested", provenance.provenance_id, provenance.evolution_identity)
    issuer = TrustedOwnerIssuer("root-1", "core-evolution", "policy-1")
    auth = issuer.issue(
        TrustedIssuerInput(approval, "root-1", "core-evolution", "policy-1", "evidence-1"),
        request_provenance=provenance.provenance_id,
        evolution_identity=provenance.evolution_identity,
    )
    validity = AuthorizationValidity("auth-attested", "policy-1", "evidence-1")
    req = ExecutionCommitRequest(
        auth,
        ExecutionIntentSnapshot.from_provenance(provenance),
        provenance.provenance_id,
        provenance.evolution_identity,
        provenance,
        validity,
    )
    require_trusted_execution(req, conn=sqlite_conn, actor="trusted-owner")
    row = sqlite_conn.execute(
        "SELECT action, resource, result FROM audit_events WHERE event_id=?",
        ("execution-authorization:auth-attested",),
    ).fetchone()
    assert tuple(row) == ("execution.authorization.consume", "auth-attested", "accepted")
