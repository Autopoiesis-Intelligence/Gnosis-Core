import pytest
from gnosis.self_learning.bridge import CoreMutationProposal, approve_core_mutation
from gnosis.self_learning.execution import bind_core_proposal
from gnosis.reflection.authority import ExecutionCommitRequest


def proposal():
    p=CoreMutationProposal("sha256:"+"0"*64,"sha256:i","sha256:v","common-self-learning","merge")
    # use factory-derived identity rather than the placeholder above
    from gnosis.self_learning.integration import IntegrationRecord
    from gnosis.self_learning.bridge import create_core_mutation_proposal
    return approve_core_mutation(create_core_mutation_proposal(IntegrationRecord("sha256:i","sha256:p","sha256:v","common-self-learning","merge")),approver="test")


def request(evolution="e"):
    return ExecutionCommitRequest(authorization=object(),intent_snapshot=object(),request_provenance="p",evolution_identity=evolution,provenance=object(),authorization_validity=AuthorizationValidity("auth","policy","evidence"))


def test_mutation_identity_cannot_be_rewritten_after_approval():
    p=proposal()
    forged=CoreMutationProposal(p.mutation_id,p.integration_id,p.version_id,p.target,"different-action","APPROVED",p.authority)
    with pytest.raises(ValueError,match="proposal identity"):
        bind_core_proposal(forged,request())


def test_foreign_execution_identity_is_bound_to_request_not_source():
    p=proposal()
    b=bind_core_proposal(p,request("foreign-evolution"))
    assert b.evolution_identity == "foreign-evolution"
    assert b.proposal_id == p.mutation_id


def test_tampered_proposal_id_is_rejected_before_binding():
    p=proposal()
    forged=CoreMutationProposal("sha256:"+"f"*64,p.integration_id,p.version_id,p.target,p.action,"APPROVED",p.authority)
    with pytest.raises(ValueError,match="proposal identity"):
        bind_core_proposal(forged,request())
