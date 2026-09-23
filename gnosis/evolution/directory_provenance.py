"""Directory optimization provenance helpers.

The helper deliberately adapts directory candidates to the existing generic
provenance contract without granting mutation authority.
"""
from __future__ import annotations

from typing import Any, Mapping

from .directory_candidate import OptimizationCandidate
from .provenance import EvidenceProvenance, build_provenance, canonical_digest


def directory_evidence(candidate: OptimizationCandidate) -> dict[str, Any]:
    return {
        "kind": "directory_optimization",
        "candidate_id": candidate.candidate_id,
        "candidate_binding_digest": candidate.candidate_binding_digest,
        "content_digest": candidate.content_digest,
        "files": candidate.files,
        "removable": candidate.removable,
        "blocked": candidate.blocked,
        "reason": candidate.reason,
    }


def build_directory_provenance(
    *,
    candidate: OptimizationCandidate,
    parent_state_id: str,
    parent_state_digest: str,
    proposed_state_digest: str,
    evaluation_status: str = "PENDING",
    shadow_status: str = "NOT_RUN",
    invariant_status: str = "PENDING",
    governance_decision: str = "PENDING",
) -> EvidenceProvenance:
    observations = directory_evidence(candidate)
    evidence_digest = canonical_digest(observations)
    return build_provenance(
        candidate_id=candidate.candidate_id,
        parent_state_id=parent_state_id,
        parent_state_digest=parent_state_digest,
        proposed_state_digest=proposed_state_digest,
        observations=observations,
        evidence_digest=evidence_digest,
        candidate_binding_digest=candidate.candidate_binding_digest,
        evaluation_status=evaluation_status,
        shadow_status=shadow_status,
        invariant_status=invariant_status,
        governance_decision=governance_decision,
    )


def verify_directory_provenance(
    provenance: EvidenceProvenance,
    candidate: OptimizationCandidate,
    *,
    parent_state_id: str,
    parent_state_digest: str,
    proposed_state_digest: str,
    evaluation_status: str,
    shadow_status: str,
    invariant_status: str,
    governance_decision: str,
) -> bool:
    observations = directory_evidence(candidate)
    expected_digest = canonical_digest(observations)
    if provenance.candidate_id != candidate.candidate_id:
        return False
    if provenance.candidate_binding_digest != candidate.candidate_binding_digest:
        return False
    if provenance.evidence_digest != expected_digest:
        return False
    return provenance.provenance_id == build_directory_provenance(
        candidate=candidate,
        parent_state_id=parent_state_id,
        parent_state_digest=parent_state_digest,
        proposed_state_digest=proposed_state_digest,
        evaluation_status=evaluation_status,
        shadow_status=shadow_status,
        invariant_status=invariant_status,
        governance_decision=governance_decision,
    ).provenance_id
