"""Deterministic, authority-free governance gate for directory optimization."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from .directory_evaluation import DirectoryShadowEvaluation

class GovernanceDecision(str, Enum):
    ALLOW = "ALLOW"
    REJECT = "REJECT"
    DEFER = "DEFER"

@dataclass(frozen=True)
class DirectoryGovernanceDecision:
    decision: GovernanceDecision
    reasons: tuple[str, ...]

def govern_directory_shadow(evaluation: DirectoryShadowEvaluation, *, evidence_complete: bool) -> DirectoryGovernanceDecision:
    if not evidence_complete:
        return DirectoryGovernanceDecision(GovernanceDecision.DEFER, ("evidence incomplete",))
    if not evaluation.accepted:
        return DirectoryGovernanceDecision(GovernanceDecision.REJECT, evaluation.reasons or ("shadow evaluation rejected",))
    return DirectoryGovernanceDecision(GovernanceDecision.ALLOW, ())
