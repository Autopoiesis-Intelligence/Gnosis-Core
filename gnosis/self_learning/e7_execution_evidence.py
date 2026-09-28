"""E7 execution outcome classification.

The classifier is deliberately evidence-first: a terminal workflow conclusion
without observable execution evidence is not a causal failure.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExecutionStatus(str, Enum):
    PASS = "PASS"
    FAIL_WITH_EVIDENCE = "FAIL_WITH_EVIDENCE"
    UNOBSERVABLE_FAILURE = "UNOBSERVABLE_FAILURE"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class ExecutionEvidence:
    status: str
    conclusion: str | None
    steps_observed: bool
    logs_observed: bool
    failure_output_observed: bool = False

    @property
    def classification(self) -> ExecutionStatus:
        if self.conclusion == "cancelled":
            return ExecutionStatus.CANCELLED
        if self.conclusion == "success":
            return ExecutionStatus.PASS
        if (
            self.conclusion == "failure"
            and self.steps_observed
            and self.logs_observed
            and self.failure_output_observed
        ):
            return ExecutionStatus.FAIL_WITH_EVIDENCE
        if self.conclusion == "failure":
            return ExecutionStatus.UNOBSERVABLE_FAILURE
        return ExecutionStatus.UNOBSERVABLE_FAILURE

    @property
    def permits_causal_attribution(self) -> bool:
        return self.classification == ExecutionStatus.FAIL_WITH_EVIDENCE
