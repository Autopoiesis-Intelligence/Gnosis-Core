"""Read-only diagnostic corpus for the Core.

The corpus owns no mutation or authorization path. It exposes the existing
endogenous gap detector to Core runtime code so development memory is not a
runtime dependency.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from gnosis.evolution.gap import GapDetector, GapHypothesis


@dataclass(frozen=True)
class DiagnosticObservation:
    kind: str
    status: str
    reason: str
    record_id: str


class DiagnosticCorpus:
    """Bounded read-only view used by the autonomous Core runtime."""

    def __init__(self, detector: GapDetector | None = None) -> None:
        self._detector = detector or GapDetector()

    def detect(
        self,
        *,
        history: Sequence[Mapping[str, Any]],
        evidence: Sequence[Mapping[str, Any]] = (),
        tensions: Sequence[Mapping[str, Any]] = (),
        forecast_errors: Sequence[Mapping[str, Any]] = (),
        minimum_repetitions: int = 2,
    ) -> tuple[GapHypothesis, ...]:
        return self._detector.detect(
            history=history,
            evidence=evidence,
            tensions=tensions,
            forecast_errors=forecast_errors,
            minimum_repetitions=minimum_repetitions,
        )
