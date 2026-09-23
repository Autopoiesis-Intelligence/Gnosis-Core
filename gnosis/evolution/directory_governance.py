"""Evidence-bound governance decision for directory optimization."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from .directory_evaluation import DirectoryShadowEvaluation
from .directory_provenance import canonical_digest

class GovernanceDecision(str, Enum):
    ALLOW = "ALLOW"
    REJECT = "REJECT"
    DEFER = "DEFER"

@dataclass(frozen=True)
class DirectoryGovernanceDecision:
    decision: GovernanceDecision
    reasons: tuple[str, ...]
    decision_digest: str

def _digest(evaluation: DirectoryShadowEvaluation, decision: GovernanceDecision) -> str:
    payload = {
        "decision": decision.value,
        "structural_accepted": evaluation.structural.accepted,
        "removed_paths": evaluation.semantic.removed_paths,
        "resource_delta": (evaluation.resource_delta.files, evaluation.resource_delta.bytes, evaluation.resource_delta.work_units),
        "reasons": evaluation.reasons,
    }
    return canonical_digest(payload)

def govern_directory_shadow(evaluation: DirectoryShadowEvaluation, *, evidence_complete: bool) -> DirectoryGovernanceDecision:
    if not evidence_complete:
        decision, reasons = GovernanceDecision.DEFER, ("evidence incomplete",)
    elif not evaluation.accepted:
        decision, reasons = GovernanceDecision.REJECT, (evaluation.reasons or ("shadow evaluation rejected",))
    else:
        decision, reasons = GovernanceDecision.ALLOW, ()
    return DirectoryGovernanceDecision(decision, reasons, _digest(evaluation, decision))
