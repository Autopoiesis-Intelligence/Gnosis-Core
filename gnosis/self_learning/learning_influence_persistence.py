"""R3.2 persistence/restart-style learning influence proof.

The proof uses the repository's existing feedback admission boundary and models
the durable handoff explicitly. It never grants mutation authority.
"""
from __future__ import annotations

from dataclasses import dataclass

from .feedback_cycle_bridge import start_cycle_from_feedback
from .feedback_integration import admit_feedback


@dataclass(frozen=True)
class PersistedLearningEvidence:
    admission_id: str
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class RestartedCycle:
    cycle_id: str
    input_refs: tuple[str, ...]
    parent_memory_entry_id: str


def persist_learning_evidence(*, admission) -> PersistedLearningEvidence:
    if admission.status != "ADMITTED":
        raise ValueError("only admitted evidence may be persisted")
    return PersistedLearningEvidence(
        admission_id=admission.admission_id,
        evidence_refs=admission.evidence_refs,
    )


def restart_cycle_from_persisted_evidence(
    *,
    persisted: PersistedLearningEvidence,
    parent_cycle_id: str,
    parent_state_digest: str,
    scope: str = "sandbox",
) -> RestartedCycle:
    # Reconstruct the admission from its persisted identity/evidence.
    admission = admit_feedback(
        feedback_id="persisted:" + persisted.admission_id,
        contract_id="contract:e806",
        scope=scope,
        verdict="FAIL",
        evidence_refs=persisted.evidence_refs,
        learning_class="COUNTEREXAMPLE",
        status="ADMITTED",
    )
    _, cycle = start_cycle_from_feedback(
        admission=admission,
        parent_cycle_id=parent_cycle_id,
        parent_state_digest=parent_state_digest,
        input_refs=persisted.evidence_refs,
        scope=scope,
    )
    return RestartedCycle(
        cycle_id=cycle.cycle_id,
        input_refs=cycle.input_refs,
        parent_memory_entry_id=cycle.parent_memory_entry_id,
    )
