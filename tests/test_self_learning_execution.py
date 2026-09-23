import pytest

from gnosis.self_learning.governance import create_review
from gnosis.self_learning.proposals import propose_from_finding
from gnosis.self_learning.validation import validate_proposal
from gnosis.self_learning.execution import create_execution_plan, serialize_plan


def _review(decision="ACCEPTED"):
    finding = "STATUS_DRIFT:E7.01:registry=X:artifact=Y"
    proposal = propose_from_finding(finding)
    validation = validate_proposal(proposal, known_contract_ids=["E7.01"], known_findings=[finding])
    return create_review(
        proposal, validation, decision=decision, reviewer="r",
        reason="evidence sufficient", created_at="2026-09-23T12:00:00+00:00"
    )


def test_accepted_review_creates_deterministic_plan():
    review = _review()
    a = create_execution_plan(review)
    b = create_execution_plan(review)
    assert a == b
    assert a.status == "PLANNED"
    assert a.authority == "execution-plan-only"
    assert "external_execution_authority_required" in a.preconditions
    assert serialize_plan(a) == serialize_plan(b)


@pytest.mark.parametrize("decision", ["REJECTED", "DEFERRED"])
def test_nonaccepted_review_cannot_create_plan(decision):
    with pytest.raises(ValueError, match="ACCEPTED"):
        create_execution_plan(_review(decision))


def test_plan_does_not_change_governance_record():
    review = _review()
    create_execution_plan(review)
    assert review.decision == "ACCEPTED"
    assert review.authority == "governance-record-only"
