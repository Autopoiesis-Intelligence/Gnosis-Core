"""E7.108 authoritative execution record for bounded proof runs."""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Mapping

from gnosis.evolution.provenance import canonical_digest


class ExecutionState(str, Enum):
    PLANNED = "PLANNED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    INTERRUPTED = "INTERRUPTED"


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
    environment_identity: Mapping[str, str]
    commands: tuple[str, ...]
    candidate_selection_id: str
    baseline_id: str
    evidence_policy_revision: str
    verification_matrix_revision: str
    criteria: tuple[CriterionEvidence, ...]
    state: ExecutionState

    @property
    def execution_id(self) -> str:
        """Canonical identity of the immutable execution context."""
        return "e7-execution:" + canonical_digest(
            {
                "batch_id": self.batch_id,
                "target_commit_sha": self.target_commit_sha,
                "repository_ref": self.repository_ref,
                "environment_identity": dict(self.environment_identity),
                "commands": self.commands,
                "candidate_selection_id": self.candidate_selection_id,
                "baseline_id": self.baseline_id,
                "evidence_policy_revision": self.evidence_policy_revision,
                "verification_matrix_revision": self.verification_matrix_revision,
            }
        )[:24]

    @property
    def terminal(self) -> bool:
        return self.state in {
            ExecutionState.COMPLETED,
            ExecutionState.FAILED,
            ExecutionState.INTERRUPTED,
        }

    @property
    def passed(self) -> bool:
        return (
            self.state is ExecutionState.COMPLETED
            and bool(self.criteria)
            and all(c.passed for c in self.criteria)
        )


def complete(
    record: ExecutionRecord, criteria: tuple[CriterionEvidence, ...]
) -> ExecutionRecord:
    if not criteria:
        raise ValueError("criterion evidence is required")
    if not all(c.evidence_id for c in criteria):
        raise ValueError("every criterion requires evidence")
    return replace(
        record,
        criteria=criteria,
        state=ExecutionState.COMPLETED,
    )
