import pytest
from gnosis.self_learning.bridge import approve_core_mutation, create_core_mutation_proposal
from gnosis.self_learning.cycle import build_verified_cycle
from gnosis.self_learning.execution import execute_approved_core_proposal
from gnosis.reflection.authority import (
    ExecutionAuthorization, ExecutionCommitRequest, ExecutionIntentSnapshot,
)
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.storage.database import connect

def valid_proposal():
    cycle = build_verified_cycle(
        "subject-test", knowledge={"rule": "bounded"}, reason="generalizable"
    )
    return approve_core_mutation(
        create_core_mutation_proposal(cycle.integration), approver="test"
    )

def test_execution_adapter_fails_closed_without_owner_authorization():
    proposal=valid_proposal()
    auth=ExecutionAuthorization(
        request_provenance="p",
        owner_approved=False,
        evolution_identity="e",
        approval_id="auth-1",
    )
    snapshot=ExecutionIntentSnapshot(
        provenance_id="p", execution_id="x",
        parent_state_id="parent", parent_state_digest="sha256:p",
        evolution_identity="e", candidate_binding_digest="sha256:c",
        proposed_state_content_id="sha256:content",
    )
    validity=AuthorizationValidity("auth-1","policy-1","ev-1")
    request=ExecutionCommitRequest(auth,snapshot,"p","e",object(),validity)
    conn = connect()
    try:
        with pytest.raises(PermissionError, match="execution authorization does not match evolution"):
            execute_approved_core_proposal(
                proposal,request,conn=conn,instance=object(),
                candidate=object(),record=object(),actor="test"
            )
    finally:
        conn.close()
