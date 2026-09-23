"""Evidence-bound governance decision for directory optimization."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from .directory_evaluation import DirectoryShadowEvaluation
from .directory_provenance import canonical_digest
from .provenance import EvidenceProvenance

class GovernanceDecision(str, Enum):
    ALLOW = "ALLOW"
    REJECT = "REJECT"
    DEFER = "DEFER"

@dataclass(frozen=True)
class DirectoryGovernanceDecision:
    decision: GovernanceDecision
    reasons: tuple[str, ...]
    decision_digest: str
    candidate_id: str
    candidate_binding_digest: str
    provenance_id: str
    evidence_digest: str

def _digest(evaluation: DirectoryShadowEvaluation, decision: GovernanceDecision, provenance: EvidenceProvenance) -> str:
    payload = {
        "candidate_id": provenance.candidate_id,
        "candidate_binding_digest": provenance.candidate_binding_digest,
        "provenance_id": provenance.provenance_id,
        "evidence_digest": provenance.evidence_digest,
        "decision": decision.value,
        "structural_accepted": evaluation.structural.accepted,
        "removed_paths": evaluation.semantic.removed_paths,
        "resource_delta": (evaluation.resource_delta.files, evaluation.resource_delta.bytes, evaluation.resource_delta.work_units),
        "reasons": evaluation.reasons,
    }
    return canonical_digest(payload)

def govern_directory_shadow(evaluation: DirectoryShadowEvaluation, *, provenance: EvidenceProvenance, evidence_complete: bool) -> DirectoryGovernanceDecision:
    if not evidence_complete:
        decision, reasons = GovernanceDecision.DEFER, ("evidence incomplete",)
    elif not evaluation.accepted:
        decision, reasons = GovernanceDecision.REJECT, evaluation.reasons or ("shadow evaluation rejected",)
    else:
        decision, reasons = GovernanceDecision.ALLOW, ()
    return DirectoryGovernanceDecision(
        decision=decision, reasons=reasons,
        decision_digest=_digest(evaluation, decision, provenance),
        candidate_id=provenance.candidate_id,
        candidate_binding_digest=provenance.candidate_binding_digest,
        provenance_id=provenance.provenance_id,
        evidence_digest=provenance.evidence_digest,
    )
