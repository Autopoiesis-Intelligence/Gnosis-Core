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
    evaluation_status: str | None = None,
    shadow_status: str | None = None,
    invariant_status: str | None = None,
    governance_decision: str | None = None,
    proposed_state_content_id: str | None = None,
    candidate_binding_digest: str | None = None,
) -> ReplayResult:
    """Fail closed unless evidence, provenance, audit and independent evaluation facts agree.

    Evaluation and governance facts must be supplied by the caller from the
    separately held evaluator/governance results. Reusing values read from the
    provenance object would only validate that object's internal consistency.
    Candidate content and binding digests must likewise come from a separately held
    candidate, not be copied from provenance. This check does not establish that
    the sandbox independently observed governance.
    A reproducible result is evidence consistency, not execution authority.
    """
    reasons: list[str] = []
    if provenance is None:
        reasons.append("provenance missing")
    if audit_record is None:
        reasons.append("audit record missing")
    evidence = replay_evidence(execution, observations)
    reasons.extend(evidence.reasons)
    independent_facts = (evaluation_status, shadow_status, invariant_status, governance_decision)
    if any(value is None for value in independent_facts):
        reasons.append("independent evaluation/governance evidence missing")
    if proposed_state_content_id is None or candidate_binding_digest is None:
        reasons.append("independent candidate-binding evidence missing")
    if provenance is not None:
        check = crosscheck_provenance(
            provenance=provenance,
            candidate_id=execution.candidate_id,
            parent_state_id=execution.parent_state_id,
            parent_state_digest=execution.parent_state_digest,
            proposed_state_digest=execution.proposed_state_digest,
            observations=observations,
            evidence_digest=execution.evidence_digest,
            execution_id_value=execution_id(
                execution.candidate_id,
                execution.parent_state_id,
                execution.evidence_digest,
                execution.parent_state_digest,
                execution.proposed_state_digest,
            ),
            # SandboxExecution contains observed execution facts only. Evaluation
            # and governance are separate provenance facts, not sandbox fields.
            evaluation_status=evaluation_status or "",
            shadow_status=shadow_status or "",
            invariant_status=invariant_status or "",
            governance_decision=governance_decision or "",
            proposed_state_content_id=proposed_state_content_id or "",
            candidate_binding_digest=candidate_binding_digest or "",
            evaluator_identity_ref=provenance.evaluator_identity_ref,
            evaluator_identity_version=provenance.evaluator_identity_version,
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
        expected_execution_id = execution_id(
            execution.candidate_id,
            execution.parent_state_id,
            execution.evidence_digest,
            execution.parent_state_digest,
            execution.proposed_state_digest,
        )
        if audit_record.execution_id != expected_execution_id:
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
