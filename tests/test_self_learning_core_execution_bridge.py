import pytest
from gnosis.self_learning.bridge import CoreMutationProposal, approve_core_mutation, create_core_mutation_proposal
from gnosis.self_learning.integration import IntegrationRecord

from gnosis.self_learning.execution import bind_core_proposal
from gnosis.reflection.authority import ExecutionCommitRequest
from gnosis.reflection.authorization_validity import AuthorizationValidity

def valid_proposal():
    record=IntegrationRecord("sha256:i","sha256:p","sha256:v","common-self-learning","merge")
    return approve_core_mutation(create_core_mutation_proposal(record), approver="test")

def req():
    return ExecutionCommitRequest(
        authorization=object(), intent_snapshot=object(),
        request_provenance="p", evolution_identity="e", provenance=object(),
        authorization_validity=AuthorizationValidity("auth","policy","evidence")
    )

def test_approved_proposal_can_bind_to_execution():
    p=valid_proposal()
    b=bind_core_proposal(p,req())
    assert b.proposal_id==p.mutation_id
    assert b.evolution_identity=="e"

def test_unapproved_proposal_is_blocked():
    p=CoreMutationProposal("m","i","v","common-self-learning","merge","PROPOSED")
    with pytest.raises(PermissionError):
        bind_core_proposal(p,req())


def test_e7_58_tampered_proposal_identity_is_rejected_before_approval():
    p=CoreMutationProposal(
        "sha256:tampered",
        "sha256:i",
        "sha256:v",
        "common-self-learning",
        "merge",
        "PROPOSED",
    )
    with pytest.raises(ValueError, match="proposal identity"):
        approve_core_mutation(p, approver="test")
