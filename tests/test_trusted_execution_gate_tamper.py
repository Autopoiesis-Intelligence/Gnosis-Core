import pytest
from dataclasses import FrozenInstanceError
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.authority import ExecutionAuthorization, ExecutionCommitRequest, ExecutionIntentSnapshot
from gnosis.reflection.trusted_execution_gate import require_trusted_execution
from gnosis.reflection.policy_identity import PolicyIdentity


def make_request(provenance, validity):
    auth=ExecutionAuthorization(request_provenance=provenance.provenance_id,owner_approved=True,evolution_identity=provenance.evolution_identity,approval_id=validity.authorization_id,policy_identity=PolicyIdentity.from_material(policy_version="policy-1",execution_scope="evolution.commit"))
    return ExecutionCommitRequest(auth,ExecutionIntentSnapshot.from_provenance(provenance),provenance.provenance_id,provenance.evolution_identity,provenance,validity)


def test_validity_is_immutable(provenance):
    v=AuthorizationValidity("auth-t","policy-1","ev-1")
    with pytest.raises(FrozenInstanceError):
        v.authorization_id="forged"


def test_tampered_policy_is_rejected_before_consumption(sqlite_conn, provenance):
    v=AuthorizationValidity("auth-t","policy-forged","ev-1")
    req=make_request(provenance,v)
    with pytest.raises(PermissionError):
        require_trusted_execution(req,conn=sqlite_conn,actor="trusted-owner")
    row=sqlite_conn.execute("SELECT event_hash FROM audit_events WHERE event_id=?",("execution-authorization:auth-t",)).fetchone()
    assert row is None


def test_tampered_policy_after_issuance_is_rejected_before_consumption(sqlite_conn, provenance):
    auth=make_request(provenance, AuthorizationValidity("auth-issued","policy-1","ev-1")).authorization
    forged=ExecutionAuthorization(
        request_provenance=auth.request_provenance,
        owner_approved=auth.owner_approved,
        evolution_identity=auth.evolution_identity,
        approval_id=auth.approval_id,
        policy_identity=PolicyIdentity.from_material(policy_version="policy-forged",execution_scope="evolution.commit"),
    )
    validity=AuthorizationValidity("auth-issued","policy-1","ev-1")
    req=ExecutionCommitRequest(forged,ExecutionIntentSnapshot.from_provenance(provenance),provenance.provenance_id,provenance.evolution_identity,provenance,validity)
    with pytest.raises(PermissionError,match="policy mismatch"):
        require_trusted_execution(req,conn=sqlite_conn,actor="trusted-owner")
    row=sqlite_conn.execute("SELECT event_hash FROM audit_events WHERE event_id=?",("execution-authorization:auth-issued",)).fetchone()
    assert row is None
