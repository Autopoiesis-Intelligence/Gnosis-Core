import pytest
from gnosis.evolution.federation_admission import admit_federation_evidence, build_core_provenance
from registry.core_handoff import create_handoff
from dataclasses import FrozenInstanceError
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.authority import ExecutionAuthorization, ExecutionCommitRequest, ExecutionIntentSnapshot
from gnosis.reflection.trusted_execution_gate import require_trusted_execution


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
        require_trusted_execution(req,conn=sqlite_conn,actor="trusted-owner")
    row=sqlite_conn.execute("SELECT event_hash FROM audit_events WHERE event_id=?",("execution-authorization:auth-t",)).fetchone()
    assert row is None




def build_provenance():
    handoff=create_handoff({"result":"AUTHORIZED","authorization_sha256":"a"*64},{"candidate_id":"c1","source_id":"s1","resource_id":"r1"},"core-evolution","propose",["e1"])["handoff"]
    env=admit_federation_evidence(handoff,{"observation":"value"})
    return build_core_provenance(env,parent_state_id="p1",parent_state_digest="pd",proposed_state_digest="qd",proposed_state_content_id="content",candidate_binding_digest="binding",evaluation_status="PASS",shadow_status="PASS",invariant_status="PASS",governance_decision="ALLOW")


def test_direct_execution_authorization_is_rejected_without_issuer_proof(sqlite_conn):
    provenance=build_provenance()
    validity=AuthorizationValidity("auth-direct", "policy-1", "ev-1")
    req=make_request(provenance, validity)
    with pytest.raises(PermissionError, match="issuer"):
        require_trusted_execution(req, conn=sqlite_conn, actor="trusted-owner")


def test_valid_authorization_rejects_substituted_policy_and_evidence(sqlite_conn):
    provenance=build_provenance()
    validity=AuthorizationValidity("auth-substitution", "policy-forged", "evidence-forged")
    req=make_request(provenance, validity)
    with pytest.raises(PermissionError, match="issued|policy|evidence"):
        require_trusted_execution(req, conn=sqlite_conn, actor="trusted-owner")
