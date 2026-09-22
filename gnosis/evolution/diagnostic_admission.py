"""Admission authority for durable Core diagnostic evidence."""
from __future__ import annotations

from .evaluator import EvaluationResult
from .provenance import DiagnosticEvidence
from .replay import ReplayResult


class DiagnosticEvidenceAdmission:
    """Fail-closed lifecycle admission; callers cannot self-assert verification."""

    def admit_observed(self, evidence: DiagnosticEvidence) -> DiagnosticEvidence:
        if evidence.lifecycle != "EPHEMERAL":
            raise ValueError("observed admission requires EPHEMERAL evidence")
        return evidence.advance("OBSERVED")

    def admit_reproduced(self, evidence: DiagnosticEvidence, replay: ReplayResult) -> DiagnosticEvidence:
        if evidence.lifecycle != "OBSERVED" or not replay.reproducible:
            raise ValueError("reproduction admission failed")
        return evidence.advance("REPRODUCED")

    def admit_verified(
        self,
        evidence: DiagnosticEvidence,
        replay: ReplayResult,
        evaluation: EvaluationResult,
    ) -> DiagnosticEvidence:
        if evidence.lifecycle != "REPRODUCED":
            raise ValueError("verification requires REPRODUCED evidence")
        if not replay.reproducible:
            raise ValueError("verification replay failed")
        if evaluation.status != "PASS" or evaluation.evidence_digest != evidence.evidence_digest:
            raise ValueError("verification evaluation failed")
        return evidence.advance("VERIFIED")

    def admit_durable(self, evidence: DiagnosticEvidence) -> DiagnosticEvidence:
        if evidence.lifecycle != "VERIFIED":
            raise ValueError("durable admission requires VERIFIED evidence")
        return evidence.advance("DURABLE")
