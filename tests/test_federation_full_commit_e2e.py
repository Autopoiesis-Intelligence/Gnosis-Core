"""R2 adversarial proof: Federation evidence may reach Core commit only through every trust gate."""
import pytest
from gnosis.evolution.federation_admission import admit_federation_evidence, build_core_provenance
from gnosis.reflection.authority import (
    ExecutionAuthorization,
    ExecutionCommitRequest,
    ExecutionIntentSnapshot,
    require_execution_candidate_binding,
)
from registry.core_handoff import create_handoff


def build_request():
    h=create_handoff({"result":"AUTHORIZED","authorization_sha256":"a"*64},{"candidate_id":"c1","source_id":"s1","resource_id":"r1"},"core-evolution","propose",["e1"])["handoff"]
    env=admit_federation_evidence(h,{"observation":"value"})
    p=build_core_provenance(env,parent_state_id="p1",parent_state_digest="pd",proposed_state_digest="qd",proposed_state_content_id="content",candidate_binding_digest="binding",evaluation_status="PASS",shadow_status="PASS",invariant_status="PASS",governance_decision="ALLOW")
    v=AuthorizationValidity("auth-e2e","policy-1","ev-1")
    a=ExecutionAuthorization(request_provenance=p.provenance_id,owner_approved=True,evolution_identity=p.evolution_identity,approval_id=v.authorization_id)
    req=ExecutionCommitRequest(a,ExecutionIntentSnapshot.from_provenance(p),p.provenance_id,p.evolution_identity,p,v)
    return req,p


def test_federation_provenance_does_not_authorize_candidate_substitution():
    from types import SimpleNamespace

    req, _ = build_request()
    # The trusted authorization gate validates authorization; candidate/record
    # binding is a separate commit-boundary contract and must reject substitution.
    with pytest.raises(PermissionError, match="candidate does not match"):
        require_execution_candidate_binding(
            req,
            SimpleNamespace(candidate_id="forged-candidate"),
            object(),
        )


def test_tampered_federation_candidate_is_rejected():
    h=create_handoff({"result":"AUTHORIZED","authorization_sha256":"a"*64},{"candidate_id":"c1","source_id":"s1","resource_id":"r1"},"core-evolution","propose",["e1"])["handoff"]
    h["candidate_id"]="forged"
    with pytest.raises(PermissionError):
        admit_federation_evidence(h,{"observation":"value"})
