import pytest

from gnosis.self_learning.governance import create_review
from gnosis.self_learning.proposals import propose_from_finding
from gnosis.self_learning.validation import validate_proposal


def _validated():
    finding = "STATUS_DRIFT:E7.01:registry=X:artifact=Y"
    proposal = propose_from_finding(finding)
    validation = validate_proposal(
        proposal, known_contract_ids=["E7.01"], known_findings=[finding]
    )
    return proposal, validation


def test_review_is_deterministic_for_fixed_inputs():
    proposal, validation = _validated()
    a = create_review(
        proposal, validation, decision="DEFERRED", reviewer="reviewer-1",
        reason="Needs additional evidence.", created_at="2026-09-23T12:00:00+00:00"
    )
    b = create_review(
        proposal, validation, decision="DEFERRED", reviewer="reviewer-1",
        reason="Needs additional evidence.", created_at="2026-09-23T12:00:00+00:00"
    )
    assert a == b
    assert a.authority == "governance-record-only"


def test_unvalidated_proposal_cannot_enter_review():
    proposal = propose_from_finding("CUSTOM_FINDING:E7.01")
    validation = validate_proposal(proposal, known_contract_ids=["E7.01"], known_findings=[proposal.finding])
    with pytest.raises(ValueError, match="validated"):
        create_review(proposal, validation, decision="ACCEPTED", reviewer="r", reason="ok")


def test_review_does_not_change_proposal_status():
    proposal, validation = _validated()
    review = create_review(
        proposal, validation, decision="ACCEPTED", reviewer="r", reason="evidence sufficient",
        created_at="2026-09-23T12:00:00+00:00"
    )
    assert review.decision == "ACCEPTED"
    assert proposal.status == "PROPOSED"
