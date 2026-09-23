"""Dry-run commit eligibility gate for directory self-optimization.

This module never mutates the filesystem. It validates that an ALLOW decision
is still bound to the exact candidate/provenance/shadow evidence supplied.
"""
from __future__ import annotations
from dataclasses import dataclass
from .directory_candidate import OptimizationCandidate, verify_candidate_binding, DirectoryUsage
from .directory_evaluation import DirectoryShadowEvaluation
from .directory_governance import DirectoryGovernanceDecision, GovernanceDecision
from .directory_provenance import verify_directory_provenance
from .provenance import EvidenceProvenance

@dataclass(frozen=True)
class DirectoryCommitEligibility:
    eligible: bool
    reasons: tuple[str, ...]

def verify_directory_commit_eligibility(
    candidate: OptimizationCandidate,
    usage: dict[str, DirectoryUsage],
    provenance: EvidenceProvenance,
    evaluation: DirectoryShadowEvaluation,
    decision: DirectoryGovernanceDecision,
) -> DirectoryCommitEligibility:
    reasons: list[str] = []
    if decision.decision is not GovernanceDecision.ALLOW:
        reasons.append(f"governance decision is {decision.decision.value}")
    if not evaluation.accepted:
        reasons.append("shadow evaluation is not accepted")
    if not verify_candidate_binding(candidate, usage):
        reasons.append("candidate evidence binding mismatch")
    if decision.candidate_id != candidate.candidate_id:
        reasons.append("decision candidate identity mismatch")
    if decision.candidate_binding_digest != candidate.candidate_binding_digest:
        reasons.append("decision candidate binding mismatch")
    if decision.provenance_id != provenance.provenance_id:
        reasons.append("decision provenance identity mismatch")
    if decision.evidence_digest != provenance.evidence_digest:
        reasons.append("decision evidence identity mismatch")
    if not verify_directory_provenance(
        provenance, candidate,
        parent_state_id=provenance.parent_state_id,
        parent_state_digest=provenance.parent_state_digest,
        proposed_state_digest=provenance.proposed_state_digest,
        evaluation_status=provenance.evaluation_status,
        shadow_status=provenance.shadow_status,
        invariant_status=provenance.invariant_status,
        governance_decision=provenance.governance_decision,
    ):
        reasons.append("provenance verification failed")
    return DirectoryCommitEligibility(not reasons, tuple(dict.fromkeys(reasons)))
