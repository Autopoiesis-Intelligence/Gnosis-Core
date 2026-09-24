"""Immutable governance decisions for Self-Learning proposals."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Literal

from .governance_gate import GovernanceReview
from .rule_proposals import RuleProposal
from .shadow_evaluation import ShadowEvaluation

GovernanceDecision = Literal["APPROVE", "REJECT", "DEFER"]


def _digest(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class GovernanceDecisionRecord:
    decision_id: str
    review_id: str
    proposal_id: str
    shadow_outcome: str
    decision: GovernanceDecision
    rationale: str
    provenance_refs: tuple[str, ...]
    decision_digest: str
    scope: str = "SELF_LEARNING_ONLY"

    def __post_init__(self) -> None:
        if self.scope != "SELF_LEARNING_ONLY":
            raise ValueError("governance decision cannot authorize core mutation")
        if not self.rationale.strip():
            raise ValueError("governance rationale is required")
        if not self.decision_digest.startswith("sha256:"):
            raise ValueError("invalid decision digest")


def record_governance_decision(
    review: GovernanceReview,
    proposal: RuleProposal,
    evaluation: ShadowEvaluation,
    *,
    decision: GovernanceDecision,
    rationale: str,
    provenance_refs: tuple[str, ...] = (),
) -> GovernanceDecisionRecord:
    if review.proposal_id != proposal.proposal_id or evaluation.proposal_id != proposal.proposal_id:
        raise ValueError("governance provenance mismatch")
    if review.decision != "REVIEW_REQUIRED":
        raise ValueError("review is not open for decision")
    if decision == "APPROVE" and evaluation.outcome != "ACCEPT_FOR_GOVERNANCE":
        raise ValueError("approval requires accepted shadow evaluation")
    payload = {
        "review_id": review.review_id,
        "proposal_id": proposal.proposal_id,
        "shadow_outcome": evaluation.outcome,
        "decision": decision,
        "rationale": rationale,
        "provenance_refs": provenance_refs,
    }
    digest = _digest(payload)
    return GovernanceDecisionRecord(
        decision_id="decision:" + digest.split(":", 1)[1],
        review_id=review.review_id,
        proposal_id=proposal.proposal_id,
        shadow_outcome=evaluation.outcome,
        decision=decision,
        rationale=rationale,
        provenance_refs=provenance_refs,
        decision_digest=digest,
    )
