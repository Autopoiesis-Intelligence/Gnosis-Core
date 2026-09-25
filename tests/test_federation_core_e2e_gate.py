"""Adversarial E2E gate: Federation may reach Core provenance, never bypass authority."""
import pytest

from gnosis.evolution.federation_admission import admit_federation_evidence, build_core_provenance
from gnosis.reflection.authority import ExecutionIntentSnapshot, ExecutionCommitRequest, ExecutionAuthorization, require_execution_commit
from registry.core_handoff import create_handoff


def make_env():
    h=create_handoff({"result":"AUTHORIZED","authorization_sha256":"a"*64},{"candidate_id":"c1","source_id":"s1","resource_id":"r1"},"core-evolution","propose",["e1"])["handoff"]
    return admit_federation_evidence(h,{"observation":"value"})


def make_provenance():
    return build_core_provenance(make_env(),parent_state_id="p1",parent_state_digest="pd",proposed_state_digest="qd",proposed_state_content_id="content",candidate_binding_digest="binding",evaluation_status="PASS",shadow_status="PASS",invariant_status="PASS",governance_decision="ALLOW")


def test_federation_reaches_core_provenance_but_not_commit_authority():
    p=make_provenance()
    snapshot=ExecutionIntentSnapshot.from_provenance(p)
    assert snapshot.evolution_identity == p.evolution_identity
    auth=ExecutionAuthorization(request_provenance=p.provenance_id,evolution_identity=p.evolution_identity,owner_approved=False)
    request=ExecutionCommitRequest(auth,snapshot,p.provenance_id,p.evolution_identity,p)
    with pytest.raises(PermissionError):
        require_execution_commit(request)


def test_tampered_federation_input_cannot_reach_provenance():
    h=create_handoff({"result":"AUTHORIZED","authorization_sha256":"a"*64},{"candidate_id":"c1","source_id":"s1","resource_id":"r1"},"core-evolution","propose",["e1"])["handoff"]
    h["candidate_id"]="forged"
    with pytest.raises(PermissionError):
        admit_federation_evidence(h,{"observation":"value"})
