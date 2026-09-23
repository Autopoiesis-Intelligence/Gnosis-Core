"""Replay checks for directory optimization evidence."""
from __future__ import annotations

from dataclasses import dataclass

from .directory_candidate import OptimizationCandidate
from .directory_provenance import verify_directory_provenance
from .provenance import execution_id


@dataclass(frozen=True)
class DirectoryReplayResult:
    reproducible: bool
    reasons: tuple[str, ...]


def verify_directory_replay(
    candidate: OptimizationCandidate,
    provenance,
    *,
    parent_state_id: str,
    parent_state_digest: str,
    proposed_state_digest: str,
    evaluation_status: str,
    shadow_status: str,
    invariant_status: str,
    governance_decision: str,
) -> DirectoryReplayResult:
    """Fail closed when a directory candidate is replayed under different state/evidence."""
    reasons: list[str] = []
    if not verify_directory_provenance(
        provenance,
        candidate,
        parent_state_id=parent_state_id,
        parent_state_digest=parent_state_digest,
        proposed_state_digest=proposed_state_digest,
        evaluation_status=evaluation_status,
        shadow_status=shadow_status,
        invariant_status=invariant_status,
        governance_decision=governance_decision,
    ):
        reasons.append("directory provenance mismatch")

    expected_execution = execution_id(
        candidate.candidate_id,
        parent_state_id,
        provenance.evidence_digest,
        parent_state_digest,
        proposed_state_digest,
    )
    if provenance.execution_id != expected_execution:
        reasons.append("directory execution identity mismatch")

    return DirectoryReplayResult(
        reproducible=not reasons,
        reasons=tuple(dict.fromkeys(reasons)),
    )
