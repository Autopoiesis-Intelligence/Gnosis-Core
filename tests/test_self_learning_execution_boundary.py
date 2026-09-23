import pytest
from gnosis.self_learning.bridge import CoreMutationProposal, approve_core_mutation
from gnosis.self_learning.execution import execute_approved_core_proposal
from gnosis.reflection.authority import (
    ExecutionAuthorization, ExecutionCommitRequest, ExecutionIntentSnapshot,
)

def test_execution_adapter_fails_closed_without_owner_authorization():
    proposal=approve_core_mutation(CoreMutationProposal("m","i","v","common-self-learning","merge"), approver="test")
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
