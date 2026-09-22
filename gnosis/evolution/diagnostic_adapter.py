"""Canonical adapter from sandbox execution evidence to diagnostic evidence."""
from __future__ import annotations

from gnosis.evidence.provenance import DiagnosticEvidence
from .sandbox import SandboxResult


def sandbox_to_diagnostic_evidence(
    result: SandboxResult,
    *,
    case_id: str,
    evidence_id: str,
) -> DiagnosticEvidence:
    execution = result.execution
    lifecycle = "OBSERVED" if result.accepted_for_evaluation and execution.status == "COMPLETED" else "EPHEMERAL"
    limitations = ()
    if execution.status != "COMPLETED":
        limitations = (f"sandbox-status:{execution.status}",)
    return DiagnosticEvidence(
        evidence_id=evidence_id,
        case_id=case_id,
        state_id=execution.parent_state_id,
        candidate_id=execution.candidate_id,
        lifecycle=lifecycle,
        observations=dict(execution.observations),
        provenance_refs=(
            f"state:{execution.parent_state_id}",
            f"state-digest:{execution.parent_state_digest}",
            f"candidate:{execution.candidate_id}",
            f"proposed-state-digest:{execution.proposed_state_digest}",
            f"sandbox-evidence:{execution.evidence_digest}",
        ),
        limitations=limitations,
    )
