"""Deterministic evaluation of sandbox evidence."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class EvaluatorIdentity:
    """Authority-relevant identity of the evaluator implementation."""
    implementation_ref: str
    implementation_version: str


CURRENT_EVALUATOR_IDENTITY = EvaluatorIdentity(
    implementation_ref="gnosis.evolution.evaluator:evaluate_observation",
    implementation_version="1",
)


@dataclass(frozen=True)
class EvaluationResult:
    status: str
    rationale: tuple[str, ...]
    evidence_digest: str
    evaluator_identity: EvaluatorIdentity


def evaluate_observation(
    observations: Mapping[str, Any],
    *,
    evidence_digest: str,
    predicate: str,
) -> EvaluationResult:
    if not evidence_digest:
        return EvaluationResult(
            "INSUFFICIENT_EVIDENCE",
            ("missing evidence digest",),
            "",
            CURRENT_EVALUATOR_IDENTITY,
        )
    if not observations:
        return EvaluationResult(
            "INSUFFICIENT_EVIDENCE",
            ("sandbox produced no observations",),
            evidence_digest,
            CURRENT_EVALUATOR_IDENTITY,
        )
    if predicate != "observations_present":
        return EvaluationResult(
            "REVIEW",
            ("evidence requires an explicit evaluator implementation",),
            evidence_digest,
            CURRENT_EVALUATOR_IDENTITY,
        )
    return EvaluationResult(
        "PASS",
        ("sandbox observations are present and digest-linked",),
        evidence_digest,
        CURRENT_EVALUATOR_IDENTITY,
    )
