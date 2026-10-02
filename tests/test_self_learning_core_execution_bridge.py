import pytest
from gnosis.self_learning.bridge import CoreMutationProposal, approve_core_mutation, create_core_mutation_proposal
from gnosis.self_learning.integration import IntegrationRecord

from gnosis.self_learning.execution import (
    bind_core_proposal,
    require_bound_core_execution,
)
from gnosis.reflection.authority import ExecutionCommitRequest


def valid_proposal():
    record = IntegrationRecord(
        "sha256:i", "sha256:p", "sha256:v", "common-self-learning", "merge"
    )
    return approve_core_mutation(create_core_mutation_proposal(record), approver="test")


def req(evolution="e"):
    return ExecutionCommitRequest(
        authorization=object(),
        intent_snapshot=object(),
        request_provenance="p",
        evolution_identity=evolution,
        provenance=object(),
    )


def test_approved_proposal_can_bind_to_execution():
    p = valid_proposal()
    b = bind_core_proposal(p, req())
    assert b.proposal_id == p.mutation_id
    assert b.evolution_identity == "e"


def test_unapproved_proposal_is_blocked():
    p = CoreMutationProposal("m", "i", "v", "common-self-learning", "merge", "PROPOSED")
    with pytest.raises(PermissionError):
        bind_core_proposal(p, req())


def test_e7_58_tampered_proposal_identity_is_rejected_before_approval():
    p = CoreMutationProposal(
        "sha256:tampered",
        "sha256:i",
        "sha256:v",
        "common-self-learning",
        "merge",
        "PROPOSED",
    )
    with pytest.raises(ValueError, match="proposal identity"):
        approve_core_mutation(p, approver="test")


def test_bound_execution_is_required_and_exactly_matches_proposal_and_request():
    p = valid_proposal()
    request = req("evolution-1")
    bound = bind_core_proposal(p, request)
    require_bound_core_execution(p, request, bound)


def test_tampered_bound_execution_is_rejected_before_commit():
    p = valid_proposal()
    request = req("evolution-1")
    bound = bind_core_proposal(p, request)

    forged = type(bound)(
        proposal_id=bound.proposal_id,
        evolution_identity=bound.evolution_identity,
        binding_digest="sha256:" + "f" * 64,
    )
    with pytest.raises(PermissionError, match="digest mismatch"):
        require_bound_core_execution(p, request, forged)


def test_bound_execution_cannot_be_reused_for_foreign_evolution():
    p = valid_proposal()
    request = req("evolution-1")
    bound = bind_core_proposal(p, request)

    with pytest.raises(PermissionError, match="evolution mismatch"):
        require_bound_core_execution(p, req("evolution-2"), bound)
