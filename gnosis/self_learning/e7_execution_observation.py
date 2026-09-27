"""E7 runtime observation classification.

Observation is deliberately distinct from execution evidence/reconciliation.
An observation may describe what was or was not observable; it never becomes
causal evidence by itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExecutionObservationStatus(str, Enum):
    PASS = "PASS"
    FAIL_WITH_EVIDENCE = "FAIL_WITH_EVIDENCE"
    UNOBSERVABLE_FAILURE = "UNOBSERVABLE_FAILURE"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class ExecutionObservation:
    status: str
    conclusion: str | None
    steps_observed: bool
    logs_observed: bool
    failure_output_observed: bool = False

    @property
    def classification(self) -> ExecutionObservationStatus:
        if self.conclusion == "cancelled":
            return ExecutionObservationStatus.CANCELLED
        if self.conclusion == "success":
            return ExecutionObservationStatus.PASS
        if (
            self.conclusion == "failure"
            and self.steps_observed
            and self.logs_observed
            and self.failure_output_observed
        ):
            return ExecutionObservationStatus.FAIL_WITH_EVIDENCE
        if self.conclusion == "failure":
            return ExecutionObservationStatus.UNOBSERVABLE_FAILURE
        return ExecutionObservationStatus.UNOBSERVABLE_FAILURE

    @property
    def permits_causal_attribution(self) -> bool:
        return self.classification == ExecutionObservationStatus.FAIL_WITH_EVIDENCE
