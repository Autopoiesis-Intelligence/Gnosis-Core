import pytest
from gnosis.self_learning.bridge import CoreMutationProposal
from gnosis.self_learning.execution import bind_core_proposal
from gnosis.reflection.authority import ExecutionCommitRequest

def req():
    return ExecutionCommitRequest(
        authorization=object(), intent_snapshot=object(),
        request_provenance="p", evolution_identity="e", provenance=object()
    )

def test_approved_proposal_can_bind_to_execution():
    p=CoreMutationProposal("m","i","v","common-self-learning","merge","APPROVED")
    b=bind_core_proposal(p,req())
    assert b.proposal_id=="m"
    assert b.evolution_identity=="e"

def test_unapproved_proposal_is_blocked():
    p=CoreMutationProposal("m","i","v","common-self-learning","merge","PROPOSED")
    with pytest.raises(PermissionError):
        bind_core_proposal(p,req())
