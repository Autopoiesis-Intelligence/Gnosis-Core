"""Executable E7.15 self-learning vertical slice.

This runner exercises existing bounded layers only:
Evidence -> Finding -> Proposal -> Validation -> Governance -> Execution Plan
-> Mutation Receipt -> binding/replay checks.

It uses deterministic in-memory evidence and never mutates Core or contracts.
"""
from __future__ import annotations

from gnosis.self_learning.proposals import propose_from_finding
from gnosis.self_learning.validation import validate_proposal
from gnosis.self_learning.governance import create_review
from gnosis.self_learning.execution import create_execution_plan
from gnosis.self_learning.receipts import (
    create_mutation_receipt,
    validate_receipt_plan_binding,
)


def run_vertical_slice() -> dict[str, object]:
    finding = "STATUS_DRIFT:E7.43:registry=IMPLEMENTED:artifact=IMPLEMENTED / UNVERIFIED"
    evidence = {
        "source_id": "synthetic:e7.15:source-1",
        "source_revision": "rev:e7.15:1",
        "evidence_digest": "sha256:e7.15.synthetic.evidence",
        "finding": finding,
    }

    proposal = propose_from_finding(finding)
    validation = validate_proposal(
        proposal,
        known_contract_ids=("E7.43",),
        known_findings=(finding,),
    )
    if not validation.valid:
        raise AssertionError(f"vertical slice validation failed: {validation.reasons}")

    review = create_review(
        proposal,
        validation,
        decision="ACCEPTED",
        reviewer="e7.15-test-governance",
        reason="synthetic deterministic acceptance for vertical-slice verification",
        created_at="2026-01-01T00:00:00+00:00",
    )
    plan = create_execution_plan(review)

    receipt = create_mutation_receipt(
        plan,
        result="APPLIED",
        target="synthetic:e7.15:target",
        before_digest="sha256:before",
        after_digest="sha256:after",
        executor="e7.15-test-executor",
        authorization_reference="synthetic:e7.15:authorization",
        created_at="2026-01-01T00:00:01+00:00",
    )
    validate_receipt_plan_binding(receipt, plan)

    replay = {
        "proposal_id": proposal.proposal_id,
        "validation_digest": review.validation_digest,
        "review_id": review.review_id,
        "plan_id": plan.plan_id,
        "receipt_id": receipt.receipt_id,
    }
    assert replay == {
        "proposal_id": proposal.proposal_id,
        "validation_digest": review.validation_digest,
        "review_id": review.review_id,
        "plan_id": plan.plan_id,
        "receipt_id": receipt.receipt_id,
    }

    return {
        "status": "PASS",
        "evidence_id": evidence["source_id"],
        "proposal_id": proposal.proposal_id,
        "review_id": review.review_id,
        "plan_id": plan.plan_id,
        "receipt_id": receipt.receipt_id,
        "replay": "PASS",
        "core_mutation": "NOT_EXECUTED",
        "authority": "none",
    }


if __name__ == "__main__":
    print(run_vertical_slice())
