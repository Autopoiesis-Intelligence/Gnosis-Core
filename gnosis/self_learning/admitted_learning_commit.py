"""Bind learning commits to an admitted evidence record."""
from __future__ import annotations

from gnosis.self_learning.learning_commit_gate import LearningCommit, commit_learning_outcome
from gnosis.self_learning.learning_evidence_admission import LearningEvidenceAdmission, may_admit

ALLOWED_CLASSES = {"LEARNING_SIGNAL", "COUNTEREXAMPLE"}

def commit_admitted_learning(
    *,
    admission: LearningEvidenceAdmission,
    source_state: str,
    closure_verified: bool,
    closure_digest: str,
    feedback_id: str,
    learning_class: str,
    status: str = "PROPOSED",
) -> LearningCommit:
    if not may_admit(admission=admission, source_state=source_state):
        raise PermissionError("learning evidence is not admitted")
    if learning_class not in ALLOWED_CLASSES:
        raise ValueError("invalid learning class")
    return commit_learning_outcome(
        closure_verified=closure_verified,
        closure_digest=closure_digest,
        feedback_id=feedback_id,
        learning_class=learning_class,
        evidence_refs=admission.evidence_refs,
        status=status,
    )

def creates_execution_authority(*, commit: LearningCommit) -> bool:
    return False
