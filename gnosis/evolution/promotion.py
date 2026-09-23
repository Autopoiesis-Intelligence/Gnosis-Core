"""Non-authoritative promotion gate.

A promotion decision is a proof obligation, never an activation authority.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class PromotionCandidate:
    candidate_id: str
    evidence_digest: str
    evaluation_status: str
    shadow_status: str
    invariant_status: str
    governance_decision: str
    authorization_scope: str = ""
    authorization_target: str = ""
    policy_version: str = ""
    authorization_freshness: str = ""
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

EVIDENCE_ROLES = frozenset({"DETECTION", "EXPLANATION", "AUTHORIZATION"})


def validate_evidence_roles(
    evidence_roles: Mapping[str, Iterable[str]],
) -> tuple[str, ...]:
    """Validate role-separated evidence without granting authority."""
    reasons: list[str] = []
    unknown = set(evidence_roles) - EVIDENCE_ROLES
    if unknown:
        reasons.append("unknown evidence role: " + ",".join(sorted(unknown)))
    for role in EVIDENCE_ROLES:
        values = tuple(evidence_roles.get(role, ()))
        if any(not value for value in values):
            reasons.append(f"{role.lower()} evidence contains empty identifier")
    return tuple(reasons)


def make_promotion_candidate(
    *,
    candidate_id: str,
    evidence_digest: str,
    evaluation_status: str,
    shadow_status: str,
    invariant_status: str,
    governance_decision: str,
    authorization_scope: str = "",
    authorization_target: str = "",
    policy_version: str = "",
    authorization_freshness: str = "",
) -> PromotionCandidate:
    if not candidate_id or not evidence_digest:
        raise ValueError("promotion candidate requires candidate_id and evidence_digest")
    raw = "|".join(
        (candidate_id, evidence_digest, evaluation_status, shadow_status,
         invariant_status, governance_decision, authorization_scope,
         authorization_target, policy_version, authorization_freshness)
    )
    return PromotionCandidate(
        "promotion:" + hashlib.sha256(raw.encode()).hexdigest()[:24],
        evidence_digest, evaluation_status, shadow_status,
        invariant_status, governance_decision, authorization_scope,
        authorization_target, policy_version, authorization_freshness,
    )


def evaluate_promotion_gate(
    candidate: PromotionCandidate,
    *,
    provenance_valid: bool,
    required_evidence: Iterable[str] = (),
    evidence_roles: Mapping[str, Iterable[str]] | None = None,
    expected_authorization_scope: str | None = None,
    expected_authorization_target: str | None = None,
    expected_policy_version: str | None = None,
    expected_authorization_freshness: str | None = None,
) -> PromotionGate:
    reasons: list[str] = []
    if evidence_roles is not None:
        reasons.extend(validate_evidence_roles(evidence_roles))
        if not tuple(evidence_roles.get("DETECTION", ())):
            reasons.append("detection evidence is missing")
        if not tuple(evidence_roles.get("EXPLANATION", ())):
            reasons.append("explanation evidence is missing")
        if not tuple(evidence_roles.get("AUTHORIZATION", ())):
            reasons.append("authorization evidence is missing")
    if evidence_roles is not None:
        if not candidate.authorization_scope or not candidate.authorization_target:
            reasons.append("authorization scope/target is missing")
    if expected_authorization_scope is not None and candidate.authorization_scope != expected_authorization_scope:
        reasons.append("authorization scope is stale or mismatched")
    if expected_authorization_target is not None and candidate.authorization_target != expected_authorization_target:
        reasons.append("authorization target is stale or mismatched")
    if expected_policy_version is not None and candidate.policy_version != expected_policy_version:
        reasons.append("authorization policy version is stale or mismatched")
    if expected_authorization_freshness is not None and candidate.authorization_freshness != expected_authorization_freshness:
        reasons.append("authorization freshness is stale or mismatched")
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
