"""Non-authoritative promotion gate.

A promotion decision is a proof obligation, never an activation authority.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class PromotionCandidate:
    candidate_id: str
    evidence_digest: str
    evaluation_status: str
    shadow_status: str
    invariant_status: str
    governance_decision: str
    status: str = "PROPOSED"

    @property
    def can_activate(self) -> bool:
        return False


@dataclass(frozen=True)
class PromotionGate:
    eligible: bool
    reasons: tuple[str, ...]
    status: str = "REVIEW_ONLY"

    @property
    def can_activate(self) -> bool:
        return False


REQUIRED_EVALUATION = "PASS"
ALLOWED_SHADOW = frozenset({"NO_BEHAVIORAL_CHANGE", "IMPROVED"})
ALLOWED_INVARIANT = frozenset({"PRESERVED", "IMPROVED"})
ALLOWED_GOVERNANCE = frozenset({"REVIEW", "APPROVE"})


def make_promotion_candidate(
    *,
    candidate_id: str,
    evidence_digest: str,
    evaluation_status: str,
    shadow_status: str,
    invariant_status: str,
    governance_decision: str,
) -> PromotionCandidate:
    if not candidate_id or not evidence_digest:
        raise ValueError("promotion candidate requires candidate_id and evidence_digest")
    raw = "|".join(
        (candidate_id, evidence_digest, evaluation_status, shadow_status,
         invariant_status, governance_decision)
    )
    return PromotionCandidate(
        "promotion:" + hashlib.sha256(raw.encode()).hexdigest()[:24],
        evidence_digest, evaluation_status, shadow_status,
        invariant_status, governance_decision,
    )


def evaluate_promotion_gate(
    candidate: PromotionCandidate,
    *,
    provenance_valid: bool,
    required_evidence: Iterable[str] = (),
) -> PromotionGate:
    reasons: list[str] = []
    if not provenance_valid:
        reasons.append("provenance cross-check failed")
    if candidate.evaluation_status != REQUIRED_EVALUATION:
        reasons.append("evaluation is not PASS")
    if candidate.shadow_status not in ALLOWED_SHADOW:
        reasons.append("shadow result is not acceptable")
    if candidate.invariant_status not in ALLOWED_INVARIANT:
        reasons.append("invariant result is not preserved/improved")
    if candidate.governance_decision not in ALLOWED_GOVERNANCE:
        reasons.append("governance decision is not review/approve")
    required = tuple(required_evidence)
    if any(not name for name in required):
        reasons.append("required evidence contains empty identifier")
    if required and candidate.evidence_digest not in required:
        reasons.append("candidate evidence digest is not in required evidence")
    return PromotionGate(
        eligible=not reasons,
        reasons=tuple(reasons),
    )


@dataclass(frozen=True)
class PromotionHandoff:
    """Non-authoritative, provenance-bound handoff into the normal Candidate pipeline."""
    promotion_id: str
    source_candidate_id: str
    evidence_digest: str
    provenance_id: str
    proposed_state_content_id: str
    status: str = "ELIGIBLE_HANDOFF"

    @property
    def can_activate(self) -> bool:
        return False


def build_promotion_handoff(
    candidate: PromotionCandidate,
    gate: PromotionGate,
    *,
    provenance_id: str,
    proposed_state_content_id: str,
) -> PromotionHandoff:
    if not gate.eligible:
        raise ValueError("ineligible promotion cannot be handed off")
    if not provenance_id or not proposed_state_content_id:
        raise ValueError("promotion handoff requires provenance and proposed state identity")
    promotion_id = "handoff:" + hashlib.sha256(
        "|".join((
            candidate.candidate_id,
            candidate.evidence_digest,
            provenance_id,
            proposed_state_content_id,
        )).encode()
    ).hexdigest()[:24]
    return PromotionHandoff(
        promotion_id=promotion_id,
        source_candidate_id=candidate.candidate_id,
        evidence_digest=candidate.evidence_digest,
        provenance_id=provenance_id,
        proposed_state_content_id=proposed_state_content_id,
    )


def materialize_candidate_from_handoff(
    handoff: PromotionHandoff,
    *,
    parent_state_id: str,
    proposed_state: "State",
    provenance_id: str,
    source_promotion_id: str,
) -> "Candidate":
    """Construct a normal Core Candidate without granting activation authority."""
    if handoff.can_activate:
        raise ValueError("promotion handoff cannot activate")
    if handoff.provenance_id != provenance_id:
        raise ValueError("handoff provenance mismatch")
    if handoff.promotion_id != source_promotion_id:
        raise ValueError("handoff promotion identity mismatch")
    if handoff.proposed_state_content_id != proposed_state.content_id:
        raise ValueError("handoff proposed state mismatch")
    if not parent_state_id:
        raise ValueError("parent state identity is required")
    from gnosis.core.types import Candidate
    return Candidate(
        parent_state_id=parent_state_id,
        proposed_state=proposed_state,
        origin="self-learning:" + handoff.promotion_id,
        seed=None,
    )
