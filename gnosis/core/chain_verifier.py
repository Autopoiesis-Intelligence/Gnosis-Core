"""Independent verification of persisted Core evolution identity chains."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping, Sequence
from .audit import EvolutionAuditRecord, crosscheck_provenance_audit, verify_audit_chain
from .provenance import EvidenceProvenance, crosscheck_provenance

@dataclass(frozen=True)
class ChainVerification:
    valid: bool
    reasons: tuple[str, ...]

def _provenance_from_mapping(row: Mapping[str, Any]) -> EvidenceProvenance:
    return EvidenceProvenance(
        execution_id=row["execution_id"], candidate_id=row["candidate_id"],
        parent_state_id=row["parent_state_id"], parent_state_digest=row["parent_state_digest"],
        proposed_state_digest=row["proposed_state_digest"], evidence_digest=row["evidence_digest"],
        evaluation_status=row["evaluation_status"], shadow_status=row["shadow_status"],
        invariant_status=row["invariant_status"], governance_decision=row["governance_decision"],
        status=row.get("status","RECORDED"), proposed_state_content_id=row.get("proposed_state_content_id",""),
        candidate_binding_digest=row.get("candidate_binding_digest",""))

def _audit_from_mapping(row: Mapping[str, Any]) -> EvolutionAuditRecord:
    required=("sequence","event_type","candidate_id","execution_id","provenance_id",
              "parent_state_digest","proposed_state_digest","evidence_digest",
              "payload_digest","previous_digest","record_digest")
    missing=[k for k in required if k not in row]
    if missing: raise ValueError("audit record missing fields: "+",".join(missing))
    return EvolutionAuditRecord(**{k:row[k] for k in required})

def verify_persisted_chain(provenance_row: Mapping[str,Any], audit_rows: Sequence[Mapping[str,Any]], *, observations: Mapping[str,Any]) -> ChainVerification:
    reasons=[]
    try:
        provenance=_provenance_from_mapping(provenance_row)
        audits=[_audit_from_mapping(row) for row in audit_rows]
    except (KeyError,TypeError,ValueError) as exc:
        return ChainVerification(False,(f"malformed persisted chain: {exc}",))
    check=crosscheck_provenance(provenance=provenance,candidate_id=provenance.candidate_id,
        parent_state_id=provenance.parent_state_id,parent_state_digest=provenance.parent_state_digest,
        proposed_state_digest=provenance.proposed_state_digest,observations=observations,
        evidence_digest=provenance.evidence_digest,execution_id_value=provenance.execution_id,
        evaluation_status=provenance.evaluation_status,shadow_status=provenance.shadow_status,
        invariant_status=provenance.invariant_status,governance_decision=provenance.governance_decision,
        proposed_state_content_id=provenance.proposed_state_content_id,
        candidate_binding_digest=provenance.candidate_binding_digest)
    reasons.extend(check.reasons)
    if not audits: reasons.append("audit chain missing")
    else:
        ok, audit_reasons=verify_audit_chain(list(audits)); reasons.extend(audit_reasons)
        matching=[a for a in audits if a.provenance_id==provenance.provenance_id]
        if not matching: reasons.append("audit provenance link missing")
        else:
            for audit in matching: reasons.extend(crosscheck_provenance_audit(provenance,audit).reasons)
    supplied=provenance_row.get("evolution_identity")
    if supplied is not None and supplied!=provenance.evolution_identity: reasons.append("evolution identity mismatch")
    return ChainVerification(not reasons,tuple(dict.fromkeys(reasons)))
