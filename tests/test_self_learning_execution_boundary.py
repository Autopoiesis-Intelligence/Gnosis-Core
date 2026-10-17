import pytest
from gnosis.self_learning.bridge import CoreMutationProposal, approve_core_mutation, create_core_mutation_proposal
from gnosis.self_learning.integration import IntegrationRecord
from gnosis.self_learning.execution import execute_approved_core_proposal
from gnosis.reflection.authority import (
    ExecutionAuthorization, ExecutionCommitRequest, ExecutionIntentSnapshot,
)

def valid_proposal():
    record=IntegrationRecord("sha256:i","sha256:p","sha256:v","common-self-learning","merge")
    return approve_core_mutation(create_core_mutation_proposal(record), approver="test")

def test_execution_adapter_fails_closed_without_owner_authorization(sqlite_conn):
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
    with pytest.raises(PermissionError, match="authorization validity is required"):
        execute_approved_core_proposal(
            proposal,request,conn=sqlite_conn,instance=object(),
            candidate=object(),record=object(),actor="test"
        )
    assert sqlite_conn.execute("SELECT COUNT(*) FROM audit_events").fetchone()[0] == 0
