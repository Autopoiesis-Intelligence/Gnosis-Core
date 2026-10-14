import pytest
import gnosis.self_learning.execution as execution_module
from gnosis.self_learning.bridge import CoreMutationProposal, approve_core_mutation, create_core_mutation_proposal
from gnosis.self_learning.integration import IntegrationRecord
from gnosis.self_learning.execution import execute_approved_core_proposal
from gnosis.reflection.authority import (
    ExecutionAuthorization, ExecutionCommitRequest, ExecutionIntentSnapshot,
)


def valid_proposal():
    record = IntegrationRecord("sha256:i", "sha256:p", "sha256:v", "common-self-learning", "merge")
    return approve_core_mutation(create_core_mutation_proposal(record), approver="test")


def valid_request():
    auth = ExecutionAuthorization(
        request_provenance="p",
        owner_approved=False,
        evolution_identity="e",
        approval_id="",
    )
    snapshot = ExecutionIntentSnapshot(
        provenance_id="p", execution_id="x",
        parent_state_id="parent", parent_state_digest="sha256:p",
        evolution_identity="e", candidate_binding_digest="sha256:c",
        proposed_state_content_id="sha256:content",
    )
    return ExecutionCommitRequest(auth, snapshot, "p", "e", object())


def test_execution_adapter_fails_closed_without_owner_authorization():
    proposal = valid_proposal()
    with pytest.raises(PermissionError):
        execute_approved_core_proposal(
            proposal, valid_request(), conn=object(), instance=object(),
            candidate=object(), record=object(), actor="test"
        )


def test_execution_bridge_forwards_signed_authorization_and_trust_context(monkeypatch):
    proposal = valid_proposal()
    request = valid_request()
    signed_authorization = object()
    trust_context = object()
    expected_result = object()
    captured = {}

    class AdapterStub:
        def commit(self, conn, instance, candidate, record, passed_request, **kwargs):
            captured["args"] = (conn, instance, candidate, record, passed_request)
            captured["kwargs"] = kwargs
            return expected_result

    monkeypatch.setattr(execution_module, "SQLiteExecutionCommitAdapter", AdapterStub)
    conn, instance, candidate, record = object(), object(), object(), object()
    result = execute_approved_core_proposal(
        proposal, request, conn, instance, candidate, record,
        actor="test",
        production_authorization=signed_authorization,
        trust_context=trust_context,
    )

    assert result is expected_result
    assert captured["args"] == (conn, instance, candidate, record, request)
    assert captured["kwargs"] == {
        "actor": "test",
        "production_authorization": signed_authorization,
        "trust_context": trust_context,
    }
