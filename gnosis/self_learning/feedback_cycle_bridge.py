"""R3.2 bridge from verified feedback admission to the next learning cycle.

The bridge is intentionally non-authoritative: feedback can seed a learning
cycle only after evidence-gated admission. It does not authorize Core changes.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from .feedback_integration import LearningFeedbackAdmission
from .learning_cycle import LearningCycle


@dataclass(frozen=True)
class FeedbackCycleLink:
    link_id: str
    feedback_id: str
    admission_id: str
    parent_cycle_id: str
    source_evidence: tuple[str, ...]


def start_cycle_from_feedback(
    *,
    admission: LearningFeedbackAdmission,
    parent_cycle_id: str,
    parent_state_digest: str,
    input_refs: tuple[str, ...] | list[str],
    scope: str,
    cycle_revision: str = "r1",
) -> tuple[FeedbackCycleLink, LearningCycle]:
    if admission.status != "ADMITTED":
        raise ValueError("only admitted feedback may seed a learning cycle")
    if admission.learning_class not in {"LEARNING_SIGNAL", "COUNTEREXAMPLE"}:
        raise ValueError("feedback class cannot seed a learning cycle")
    if not parent_cycle_id.strip():
        raise ValueError("parent cycle identity is required")
    if not input_refs:
        raise ValueError("cycle requires input references")

    refs = tuple(sorted(set(str(x) for x in input_refs)))
    canonical = {
        "feedback_id": admission.feedback_id,
        "admission_id": admission.admission_id,
        "parent_cycle_id": parent_cycle_id,
        "parent_state_digest": parent_state_digest,
        "input_refs": refs,
        "scope": scope.strip(),
        "cycle_revision": cycle_revision,
    }
    link_id = "sha256:" + hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    # The existing LearningCycle remains the canonical cycle identity.
    cycle = LearningCycle(
        cycle_id=link_id,
        parent_memory_entry_id=admission.admission_id,
        parent_state_digest=parent_state_digest,
        input_refs=refs,
        scope=scope.strip(),
        cycle_revision=cycle_revision,
        status="STARTED",
    )
    link = FeedbackCycleLink(
        link_id=link_id,
        feedback_id=admission.feedback_id,
        admission_id=admission.admission_id,
        parent_cycle_id=parent_cycle_id,
        source_evidence=admission.evidence_refs,
    )
    return link, cycle


def learning_influence_is_bound(
    *,
    link: FeedbackCycleLink,
    admission: LearningFeedbackAdmission,
    cycle: LearningCycle,
) -> bool:
    return (
        link.feedback_id == admission.feedback_id
        and link.admission_id == admission.admission_id
        and cycle.parent_memory_entry_id == admission.admission_id
        and cycle.input_refs == tuple(sorted(set(admission.evidence_refs)))
        and cycle.cycle_id == link.link_id
    )
