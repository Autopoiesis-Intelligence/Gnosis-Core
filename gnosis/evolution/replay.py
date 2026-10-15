"""Deterministic replay and evidence-integrity checks for evolution experiments."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .audit import crosscheck_provenance_audit
from .provenance import EvidenceProvenance, canonical_digest, crosscheck_provenance, execution_id, verify_evidence_digest
from .sandbox import SandboxExecution


@dataclass(frozen=True)
class ReplayResult:
    reproducible: bool
    reasons: tuple[str, ...]
    expected_digest: str | None = None
    actual_digest: str | None = None


def replay_evidence(
    execution: SandboxExecution,
    observations: Mapping[str, Any],
) -> ReplayResult:
    """Recompute evidence identity without executing or activating anything."""
    actual = canonical_digest(observations)
    reasons: list[str] = []
    if actual != execution.evidence_digest:
        reasons.append("evidence digest mismatch")
    if not verify_evidence_digest(observations, execution.evidence_digest):
        reasons.append("evidence verification failed")
    return ReplayResult(
        reproducible=not reasons,
        reasons=tuple(reasons),
        expected_digest=execution.evidence_digest,
        actual_digest=actual,
    )


def replay_complete(
    execution: SandboxExecution,
    provenance: EvidenceProvenance | None,
    audit_record: Any | None,
    *,
    observations: Mapping[str, Any],
    evaluation: Any | None = None,
    governance: Any | None = None,
    candidate: Any | None = None,
) -> ReplayResult:
    """Fail closed unless candidate, states, evidence, evaluation, governance, provenance and audit agree."""
    reasons: list[str] = []
    if provenance is None:
        reasons.append("provenance missing")
    if audit_record is None:
        reasons.append("audit record missing")
    evidence = replay_evidence(execution, observations)
    reasons.extend(evidence.reasons)
    canonical_execution_id = execution_id(
        execution.candidate_id,
        execution.parent_state_id,
        execution.evidence_digest,
        execution.parent_state_digest,
        execution.proposed_state_digest,
    )
    if provenance is not None:
        if evaluation is None or governance is None or candidate is None:
            reasons.append("candidate, evaluation or governance evidence missing")
        else:
            if candidate.candidate_id != execution.candidate_id:
                reasons.append("candidate identity differs from sandbox execution")
            if candidate.parent_state_id != execution.parent_state_id:
                reasons.append("candidate parent differs from sandbox execution")
            if candidate.proposed_state.content_id != execution.proposed_state_digest:
                reasons.append("candidate proposed state differs from sandbox execution")
            evaluator = evaluation.evaluator_identity
            check = crosscheck_provenance(
                provenance=provenance,
                candidate_id=execution.candidate_id,
                parent_state_id=execution.parent_state_id,
                parent_state_digest=execution.parent_state_digest,
                proposed_state_digest=execution.proposed_state_digest,
                observations=observations,
                evidence_digest=execution.evidence_digest,
                execution_id_value=canonical_execution_id,
                evaluation_status=evaluation.status,
                shadow_status=governance.shadow_status,
                invariant_status=governance.invariant_status,
                governance_decision=governance.decision,
                proposed_state_content_id=candidate.proposed_state.content_id,
                candidate_binding_digest=candidate.binding_digest(execution.parent_state_digest),
                evaluator_identity_ref=evaluator.implementation_ref,
                evaluator_identity_version=evaluator.implementation_version,
            )
            reasons.extend(check.reasons)
    if audit_record is not None:
        if audit_record.candidate_id != execution.candidate_id:
            reasons.append("audit candidate mismatch")
        if provenance is None or getattr(audit_record, "provenance_id", None) != provenance.provenance_id:
            reasons.append("audit provenance mismatch")
        for field in ("parent_state_digest", "proposed_state_digest", "evidence_digest"):
            if getattr(audit_record, field, None) != getattr(execution, field, None):
                reasons.append(f"audit {field} mismatch")
        if audit_record.execution_id != canonical_execution_id:
            reasons.append("audit execution mismatch")
        if provenance is not None:
            link = crosscheck_provenance_audit(provenance, audit_record)
            reasons.extend("persisted " + reason for reason in link.reasons)
    return ReplayResult(reproducible=not reasons, reasons=tuple(dict.fromkeys(reasons)))


def replay_identity(
    execution: SandboxExecution,
    *,
    candidate_id: str,
    parent_state_id: str,
    parent_state_digest: str,
    proposed_state_digest: str,
) -> ReplayResult:
    """Check that replay inputs still identify the same execution."""
    reasons: list[str] = []
    if execution.candidate_id != candidate_id:
        reasons.append("candidate identity mismatch")
    if execution.parent_state_id != parent_state_id:
        reasons.append("parent state identity mismatch")
    if execution.parent_state_digest != parent_state_digest:
        reasons.append("parent state digest mismatch")
    if execution.proposed_state_digest != proposed_state_digest:
        reasons.append("proposed state digest mismatch")
    return ReplayResult(reproducible=not reasons, reasons=tuple(reasons))
