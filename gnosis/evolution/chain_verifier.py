"""Independent verification of persisted evolution identity chains.

This module accepts plain persisted records and does not depend on live evolution
or transaction objects. It is intentionally read-only and fail-closed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .audit import EvolutionAuditRecord, crosscheck_provenance_audit, verify_audit_chain
from .provenance import EvidenceProvenance, crosscheck_provenance
from gnosis.self_learning.e7_106_selection import SelectionRecord, assert_selection_record_matches_transition


@dataclass(frozen=True)
class ChainVerification:
    valid: bool
    reasons: tuple[str, ...]


def _provenance_from_mapping(row: Mapping[str, Any]) -> EvidenceProvenance:
    return EvidenceProvenance(
        execution_id=row["execution_id"],
        candidate_id=row["candidate_id"],
        parent_state_id=row["parent_state_id"],
        parent_state_digest=row["parent_state_digest"],
        proposed_state_digest=row["proposed_state_digest"],
        evidence_digest=row["evidence_digest"],
        evaluation_status=row["evaluation_status"],
        shadow_status=row["shadow_status"],
        invariant_status=row["invariant_status"],
        governance_decision=row["governance_decision"],
        status=row.get("status", "RECORDED"),
        proposed_state_content_id=row.get("proposed_state_content_id", ""),
        candidate_binding_digest=row.get("candidate_binding_digest", ""),
    )


def _audit_from_mapping(row: Mapping[str, Any]) -> EvolutionAuditRecord:
    required = (
        "sequence", "event_type", "candidate_id", "execution_id",
        "provenance_id", "parent_state_digest", "proposed_state_digest",
        "evidence_digest", "candidate_binding_digest", "payload_digest", "previous_digest", "record_digest",
    )
    missing = [key for key in required if key not in row]
    if missing:
        raise ValueError("audit record missing fields: " + ",".join(missing))
    return EvolutionAuditRecord(**{key: row[key] for key in required})


def verify_persisted_chain(
    provenance_row: Mapping[str, Any],
    audit_rows: Sequence[Mapping[str, Any]],
    *,
    observations: Mapping[str, Any],
) -> ChainVerification:
    """Verify persisted provenance and audit data without runtime evolution state."""
    reasons: list[str] = []
    try:
        provenance = _provenance_from_mapping(provenance_row)
        audits = [_audit_from_mapping(row) for row in audit_rows]
    except (KeyError, TypeError, ValueError) as exc:
        return ChainVerification(False, (f"malformed persisted chain: {exc}",))

    provenance_check = crosscheck_provenance(
        provenance=provenance,
        candidate_id=provenance.candidate_id,
        parent_state_id=provenance.parent_state_id,
        parent_state_digest=provenance.parent_state_digest,
        proposed_state_digest=provenance.proposed_state_digest,
        observations=observations,
        evidence_digest=provenance.evidence_digest,
        execution_id_value=provenance.execution_id,
        evaluation_status=provenance.evaluation_status,
        shadow_status=provenance.shadow_status,
        invariant_status=provenance.invariant_status,
        governance_decision=provenance.governance_decision,
        proposed_state_content_id=provenance.proposed_state_content_id,
        candidate_binding_digest=provenance.candidate_binding_digest,
    )
    reasons.extend(provenance_check.reasons)

    if not audits:
        reasons.append("audit chain missing")
    else:
        audit_ok, audit_reasons = verify_audit_chain(list(audits))
        reasons.extend(audit_reasons)
        # A provenance chain must be represented by exactly one canonical audit
        # event. Additional events are allowed in the global audit log, but only
        # the event linked to this provenance may be used as its durable record.
        matching = [a for a in audits if a.provenance_id == provenance.provenance_id]
        if len(matching) > 1:
            reasons.append("multiple audit records linked to provenance")
        if not matching:
            reasons.append("audit provenance link missing")
        else:
            for audit in matching:
                link = crosscheck_provenance_audit(provenance, audit)
                reasons.extend(link.reasons)

    expected_identity = provenance.evolution_identity
    supplied_identity = provenance_row.get("evolution_identity")
    if supplied_identity is not None and supplied_identity != expected_identity:
        reasons.append("evolution identity mismatch")
    return ChainVerification(not reasons, tuple(dict.fromkeys(reasons)))


def verify_selection_transition_binding(
    selection_record: SelectionRecord,
    transition: Any,
) -> ChainVerification:
    """Verify the frozen selection identity against a persisted transition-like record."""
    reasons: list[str] = []
    try:
        candidate_id = transition["candidate_id"] if isinstance(transition, Mapping) else transition.candidate_id
        accepted = transition["accepted"] if isinstance(transition, Mapping) else transition.accepted
    except (KeyError, AttributeError, TypeError) as exc:
        return ChainVerification(False, (f"malformed transition record: {exc}",))
    try:
        # Reconstruct only the fields needed by the existing fail-closed contract.
        # Full TransitionRecord validation remains owned by Core types.
        if isinstance(transition, Mapping):
            from gnosis.core.types import TestResult, TransitionRecord
            test_result = transition.get("test_result")
            if not isinstance(test_result, TestResult):
                test_result = TestResult(bool(accepted))
            transition_obj = TransitionRecord(
                from_state_id=transition["from_state_id"],
                to_state_id=transition["to_state_id"],
                candidate_id=candidate_id,
                test_result=test_result,
                accepted=accepted,
                reason=transition["reason"],
                test_rule_id=transition.get("test_rule_id", "test-rule:unspecified"),
            )
        else:
            transition_obj = transition
        assert_selection_record_matches_transition(selection_record, transition_obj)
    except (KeyError, TypeError, ValueError) as exc:
        reasons.append(str(exc))
    return ChainVerification(not reasons, tuple(dict.fromkeys(reasons)))


def verify_evolution_identity_chain(
    selection_record: SelectionRecord,
    transition: Any,
    provenance_row: Mapping[str, Any],
    audit_rows: Sequence[Mapping[str, Any]],
    *,
    observations: Mapping[str, Any],
) -> ChainVerification:
    """Verify Selection -> Transition -> Provenance -> Audit as one read-only chain."""
    reasons: list[str] = []

    selection_check = verify_selection_transition_binding(selection_record, transition)
    reasons.extend(selection_check.reasons)

    persisted_check = verify_persisted_chain(
        provenance_row,
        audit_rows,
        observations=observations,
    )
    reasons.extend(persisted_check.reasons)

    try:
        selected_ids = tuple(selection_record.selected_candidate_ids)
        transition_candidate = transition["candidate_id"] if isinstance(transition, Mapping) else transition.candidate_id
        transition_accepted = transition["accepted"] if isinstance(transition, Mapping) else transition.accepted
        provenance_candidate = provenance_row["candidate_id"]
        provenance_execution = provenance_row["execution_id"]
        matching = [row for row in audit_rows if row.get("provenance_id") == provenance_row.get("provenance_id")]
        if selected_ids:
            if len(selected_ids) != 1:
                reasons.append("selection must contain exactly one selected candidate")
            elif transition_candidate != selected_ids[0]:
                reasons.append("selection/transition candidate identity mismatch")
            if provenance_candidate != selected_ids[0]:
                reasons.append("selection/provenance candidate identity mismatch")
        if not transition_accepted:
            reasons.append("transition is not accepted")
        if transition_candidate != provenance_candidate:
            reasons.append("transition/provenance candidate identity mismatch")
        if not matching:
            reasons.append("provenance/audit identity link missing")
        else:
            if any(row.get("candidate_id") != provenance_candidate for row in matching):
                reasons.append("audit candidate identity mismatch")
            if any(row.get("execution_id") != provenance_execution for row in matching):
                reasons.append("audit execution identity mismatch")
    except (KeyError, AttributeError, TypeError) as exc:
        reasons.append(f"malformed evolution identity chain: {exc}")

    return ChainVerification(not reasons, tuple(dict.fromkeys(reasons)))
