"""Independent governance gate for shadow-evaluated Self-Learning proposals."""

from __future__ import annotations

from dataclasses import dataclass
from .shadow_evaluation import ShadowEvaluation
from .rule_proposals import RuleProposal


@dataclass(frozen=True)
class GovernanceReview:
    review_id: str
    proposal_id: str
    shadow_outcome: str
    decision: str
    scope: str = "SELF_LEARNING_ONLY"

    def __post_init__(self) -> None:
        if self.scope != "SELF_LEARNING_ONLY":
            raise ValueError("governance review cannot authorize core mutation")
        if self.decision not in {"REVIEW_REQUIRED", "BLOCKED"}:
            raise ValueError("governance review must remain non-authorizing")


def prepare_governance_review(proposal: RuleProposal, evaluation: ShadowEvaluation) -> GovernanceReview:
    if proposal.proposal_id != evaluation.proposal_id:
        raise ValueError("proposal/evaluation mismatch")
    if evaluation.scope != "SELF_LEARNING_ONLY":
        raise ValueError("invalid evaluation scope")
    if evaluation.outcome != "ACCEPT_FOR_GOVERNANCE":
        raise ValueError("only accepted shadow evaluations may enter governance review")
    return GovernanceReview(
        review_id=f"governance:{proposal.proposal_id}",
        proposal_id=proposal.proposal_id,
        shadow_outcome=evaluation.outcome,
        decision="REVIEW_REQUIRED",
    )
