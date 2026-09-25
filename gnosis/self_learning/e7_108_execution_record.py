"""E7.108 authoritative execution record for bounded proof runs."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Mapping

class ExecutionState(str, Enum):
    PLANNED="PLANNED"; RUNNING="RUNNING"; COMPLETED="COMPLETED"; FAILED="FAILED"; INTERRUPTED="INTERRUPTED"

@dataclass(frozen=True)
class CriterionEvidence:
    criterion_id: str
    expected: str
    observed: str
    evidence_id: str
    passed: bool

@dataclass(frozen=True)
class ExecutionRecord:
    batch_id: str
    target_commit_sha: str
    repository_ref: str
    environment_identity: Mapping[str,str]
    commands: tuple[str,...]
    candidate_selection_id: str
    baseline_id: str
    evidence_policy_revision: str
    verification_matrix_revision: str
    criteria: tuple[CriterionEvidence,...]
    state: ExecutionState

    @property
    def terminal(self) -> bool:
        return self.state in {ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.INTERRUPTED}

    @property
    def passed(self) -> bool:
        return self.state is ExecutionState.COMPLETED and bool(self.criteria) and all(c.passed for c in self.criteria)

def complete(record: ExecutionRecord, criteria: tuple[CriterionEvidence,...]) -> ExecutionRecord:
    if not criteria:
        raise ValueError("criterion evidence is required")
    if not all(c.evidence_id for c in criteria):
        raise ValueError("every criterion requires evidence")
    return ExecutionRecord(**{**record.__dict__, "criteria": criteria, "state": ExecutionState.COMPLETED})
