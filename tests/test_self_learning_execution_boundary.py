import pytest
from gnosis.self_learning.bridge import CoreMutationProposal, approve_core_mutation, create_core_mutation_proposal
from gnosis.self_learning.execution import execute_approved_core_proposal
from gnosis.reflection.authority import (
    ExecutionAuthorization, ExecutionCommitRequest, ExecutionIntentSnapshot,
)

def valid_proposal():
    from gnosis.self_learning.integration import create_integration_record
    from gnosis.self_learning.promotion import propose_promotion, decide_promotion
    from gnosis.self_learning.lineage import KnowledgeVersion

    version=KnowledgeVersion(
        "sha256:v", "u", "flow", "common", "sha256:k", "GENESIS"
    )
    promotion=propose_promotion(
        version, evidence_refs=("sha256:e",), reason="generalizable"
    )
    accepted=decide_promotion(
        promotion, decision="ACCEPTED", reviewer="test"
    )
    record=create_integration_record(accepted, action="merge")
    return approve_core_mutation(
        create_core_mutation_proposal(record), approver="test"
    )

def test_execution_adapter_fails_closed_without_owner_authorization():
    proposal=valid_proposal()
    auth=ExecutionAuthorization(
        request_provenance="p",
        owner_approved=False,
        evolution_identity="e",
        approval_id="",
    )
    snapshot=ExecutionIntentSnapshot(
        provenance_id="p", execution_id="x",
        parent_state_id="parent", parent_state_digest="sha256:p",
        evolution_identity="e", candidate_binding_digest="sha256:c",
        proposed_state_content_id="sha256:content",
    )
    request=ExecutionCommitRequest(auth,snapshot,"p","e",object())
    with pytest.raises(PermissionError):
        execute_approved_core_proposal(
            proposal,request,conn=object(),instance=object(),
            candidate=object(),record=object(),actor="test"
        )
