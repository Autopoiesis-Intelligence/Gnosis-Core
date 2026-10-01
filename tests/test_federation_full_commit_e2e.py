"""R2 adversarial proof: Federation evidence may reach Core commit only through every trust gate."""
import pytest
from gnosis.evolution.federation_admission import admit_federation_evidence, build_core_provenance
from gnosis.reflection.authority import ExecutionAuthorization, ExecutionCommitRequest, ExecutionIntentSnapshot
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.trusted_execution_gate import require_trusted_execution
from registry.core_handoff import create_handoff


def build_request():
    h=create_handoff({"result":"AUTHORIZED","authorization_sha256":"a"*64},{"candidate_id":"c1","source_id":"s1","resource_id":"r1"},"core-evolution","propose",["e1"])["handoff"]
    env=admit_federation_evidence(h,{"observation":"value"})
    p=build_core_provenance(env,parent_state_id="p1",parent_state_digest="pd",proposed_state_digest="qd",proposed_state_content_id="content",candidate_binding_digest="binding",evaluation_status="PASS",shadow_status="PASS",invariant_status="PASS",governance_decision="ALLOW")
    v=AuthorizationValidity("auth-e2e","policy-1",p.evidence_digest)
    a=ExecutionAuthorization(request_provenance=p.provenance_id,owner_approved=True,evolution_identity=p.evolution_identity,approval_id=v.authorization_id)
    req=ExecutionCommitRequest(a,ExecutionIntentSnapshot.from_provenance(p),p.provenance_id,p.evolution_identity,p,v)
    return req,p


def test_federation_e2e_reaches_trusted_gate(sqlite_conn):
    req,p=build_request()
    # The trusted gate validates and consumes the authorization artifact; concrete
    # candidate/transition binding remains the responsibility of the commit adapter.
    require_trusted_execution(req,conn=sqlite_conn,actor="trusted-owner")
    row=sqlite_conn.execute("SELECT event_hash FROM audit_events WHERE event_id=?",("execution-authorization:auth-e2e",)).fetchone()
    assert row is not None


def test_tampered_federation_candidate_is_rejected():
    h=create_handoff({"result":"AUTHORIZED","authorization_sha256":"a"*64},{"candidate_id":"c1","source_id":"s1","resource_id":"r1"},"core-evolution","propose",["e1"])["handoff"]
    h["candidate_id"]="forged"
    with pytest.raises(PermissionError):
        admit_federation_evidence(h,{"observation":"value"})
