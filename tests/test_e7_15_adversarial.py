import pytest

from gnosis.self_learning.execution import create_execution_plan
from gnosis.self_learning.proposals import propose_from_finding
from gnosis.self_learning.validation import validate_proposal
from gnosis.self_learning.governance import create_review
from gnosis.self_learning.receipts import create_mutation_receipt, validate_receipt_plan_binding


def _plan(*, reviewer="adversarial-test"):
    finding = "STATUS_DRIFT:E7.43:registry=IMPLEMENTED:artifact=IMPLEMENTED / UNVERIFIED"
    proposal = propose_from_finding(finding)
    validation = validate_proposal(
        proposal, known_contract_ids=("E7.43",), known_findings=(finding,)
    )
    review = create_review(
        proposal, validation, decision="ACCEPTED", reviewer=reviewer,
        reason="deterministic failure-injection", created_at="2026-01-01T00:00:00+00:00",
    )
    return create_execution_plan(review)


def test_receipt_cross_plan_substitution_is_rejected():
    plan = _plan()
    other = _plan(reviewer="other-reviewer")
    receipt = create_mutation_receipt(
        plan, result="APPLIED", target="target", before_digest="before",
        after_digest="after", executor="test", authorization_reference="auth",
        created_at="2026-01-01T00:00:01+00:00",
    )
    with pytest.raises(PermissionError):
        validate_receipt_plan_binding(receipt, other)


def test_applied_noop_is_rejected():
    plan = _plan()
    with pytest.raises(ValueError, match="must change"):
        create_mutation_receipt(
            plan, result="APPLIED", target="target", before_digest="same",
            after_digest="same", executor="test", authorization_reference="auth",
            created_at="2026-01-01T00:00:01+00:00",
        )


def test_unaccepted_governance_cannot_create_execution_plan():
    finding = "STATUS_DRIFT:E7.43:registry=IMPLEMENTED:artifact=IMPLEMENTED / UNVERIFIED"
    proposal = propose_from_finding(finding)
    validation = validate_proposal(
        proposal, known_contract_ids=("E7.43",), known_findings=(finding,)
    )
    review = create_review(
        proposal, validation, decision="REJECTED", reviewer="adversarial-test",
        reason="explicit rejection", created_at="2026-01-01T00:00:00+00:00",
    )
    with pytest.raises(ValueError, match="ACCEPTED"):
        create_execution_plan(review)


def test_tampered_receipt_identity_is_rejected():
    from dataclasses import replace
    plan = _plan()
    receipt = create_mutation_receipt(
        plan, result="APPLIED", target="target", before_digest="before",
        after_digest="after", executor="test", authorization_reference="auth",
        created_at="2026-01-01T00:00:01+00:00",
    )
    tampered = replace(receipt, proposal_id="sha256:forged-proposal")
    with pytest.raises(PermissionError, match="proposal identity mismatch"):
        validate_receipt_plan_binding(tampered, plan)


def test_tampered_receipt_review_identity_is_rejected():
    from dataclasses import replace
    plan = _plan()
    receipt = create_mutation_receipt(
        plan, result="APPLIED", target="target", before_digest="before",
        after_digest="after", executor="test", authorization_reference="auth",
        created_at="2026-01-01T00:00:01+00:00",
    )
    tampered = replace(receipt, review_id="sha256:forged-review")
    with pytest.raises(PermissionError, match="review identity mismatch"):
        validate_receipt_plan_binding(tampered, plan)
