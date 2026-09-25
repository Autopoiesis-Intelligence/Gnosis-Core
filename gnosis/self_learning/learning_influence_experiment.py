"""R3.2 two-cycle learning-influence experiment.

The experiment is deliberately model-level: it compares candidate inputs with
and without admitted evidence. It never mutates Core or grants authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from .feedback_cycle_bridge import start_cycle_from_feedback
from .feedback_integration import admit_feedback


@dataclass(frozen=True)
class LearningInfluenceExperiment:
    baseline_input: tuple[str, ...]
    evidence_input: tuple[str, ...]
    changed_by_admitted_evidence: bool
    influence_digest: str


def run_learning_influence_experiment(
    *,
    feedback_id: str,
    contract_id: str,
    parent_cycle_id: str,
    parent_state_digest: str,
    baseline_input: tuple[str, ...] | list[str],
    failure_evidence: tuple[str, ...] | list[str],
) -> LearningInfluenceExperiment:
    evidence = tuple(sorted(set(str(x) for x in failure_evidence)))
    if not evidence:
        raise ValueError("failure evidence is required")

    admission = admit_feedback(
        feedback_id=feedback_id,
        contract_id=contract_id,
        scope="sandbox",
        verdict="FAIL",
        evidence_refs=evidence,
        learning_class="COUNTEREXAMPLE",
        status="ADMITTED",
    )
    _, next_cycle = start_cycle_from_feedback(
        admission=admission,
        parent_cycle_id=parent_cycle_id,
        parent_state_digest=parent_state_digest,
        input_refs=evidence,
        scope="sandbox",
    )

    baseline = tuple(sorted(set(str(x) for x in baseline_input)))
    influenced = tuple(next_cycle.input_refs)
    canonical = {
        "baseline_input": baseline,
        "evidence_input": influenced,
        "admission_id": admission.admission_id,
    }
    digest = "sha256:" + hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    return LearningInfluenceExperiment(
        baseline_input=baseline,
        evidence_input=influenced,
        changed_by_admitted_evidence=baseline != influenced,
        influence_digest=digest,
    )
