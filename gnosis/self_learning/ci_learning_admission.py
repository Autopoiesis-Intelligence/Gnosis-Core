"""Bridge verified CI evidence into the existing learning admission contract."""
from __future__ import annotations

from gnosis.self_learning.ci_evidence_gate import CIEvidence, may_admit_learning
from gnosis.self_learning.learning_evidence_admission import (
    LearningEvidenceAdmission,
    create_admission,
)


def admit_ci_evidence(
    *,
    evidence: CIEvidence,
    expected_commit_sha: str,
    expected_scope: str,
    privacy_classification: str = "PUBLIC",
    learning_scope: str | None = None,
) -> LearningEvidenceAdmission:
    if not may_admit_learning(
        evidence=evidence,
        expected_commit_sha=expected_commit_sha,
        expected_scope=expected_scope,
    ):
        raise PermissionError("CI evidence is not proven for learning admission")
    scope = learning_scope or expected_scope
    return create_admission(
        source_contract_id=evidence.evidence_id,
        verification_refs=(
            f"commit:{evidence.commit_sha}",
            f"workflow:{evidence.workflow_run_id}",
            f"job:{evidence.job_id}",
        ),
        evidence_refs=(f"ci:{evidence.evidence_digest}",),
        evidence_digest=evidence.evidence_digest,
        privacy_classification=privacy_classification,
        learning_scope=scope,
        status="ADMITTED",
    )


def creates_execution_authority(*, admission: LearningEvidenceAdmission) -> bool:
    return False
