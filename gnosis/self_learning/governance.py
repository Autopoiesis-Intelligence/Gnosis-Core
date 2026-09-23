"""Governance review records for validated Self-Learning proposals.

This layer records a governance decision; it does not perform the decision.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from .proposals import ContractProposal
from .validation import ValidationResult


_ALLOWED = frozenset({"ACCEPTED", "REJECTED", "DEFERRED"})


@dataclass(frozen=True)
class GovernanceReview:
    review_id: str
    proposal_id: str
    decision: str
    reviewer: str
    reason: str
    validation_digest: str
    created_at: str
    provenance: str = "self-learning-governance-review"
    authority: str = "governance-record-only"

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def create_review(
    proposal: ContractProposal,
    validation: ValidationResult,
    *,
    decision: str,
    reviewer: str,
    reason: str,
    created_at: str | None = None,
) -> GovernanceReview:
    if not validation.valid:
        raise ValueError("only validated proposals may enter governance review")
    if decision not in _ALLOWED:
        raise ValueError(f"unsupported decision: {decision}")
    if not reviewer.strip():
        raise ValueError("reviewer must be non-empty")
    if not reason.strip():
        raise ValueError("reason must be non-empty")
    if validation.proposal_id != proposal.proposal_id:
        raise ValueError("validation/proposal identity mismatch")

    timestamp = created_at or datetime.now(timezone.utc).isoformat()
    canonical = {
        "proposal_id": proposal.proposal_id,
        "decision": decision,
        "reviewer": reviewer.strip(),
        "reason": reason.strip(),
        "validation": validation.as_dict(),
        "created_at": timestamp,
    }
    review_id = "sha256:" + hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return GovernanceReview(
        review_id=review_id,
        proposal_id=proposal.proposal_id,
        decision=decision,
        reviewer=reviewer.strip(),
        reason=reason.strip(),
        validation_digest=validation_digest(validation),
        created_at=timestamp,
    )


def validation_digest(validation: ValidationResult) -> str:
    canonical = json.dumps(validation.as_dict(), sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(canonical).hexdigest()
