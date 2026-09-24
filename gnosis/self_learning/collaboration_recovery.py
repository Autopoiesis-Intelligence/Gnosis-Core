"""Fail-closed recovery boundary for external collaboration execution (E7.78)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass

RECOVERY={"NO_ACTION","COMPENSATION_REQUIRED","COMPENSATED","MANUAL_REVIEW","COMPENSATION_FAILED","NOT_COMPENSATABLE"}

@dataclass(frozen=True)
class CollaborationRecoveryRecord:
    recovery_id:str
    evidence_id:str
    authorization_id:str
    attempt_id:str
    original_result:str
    recovery_state:str
    compensation_contract_id:str
    compensation_target:str
    reason:str
    prior_evidence_digest:str
    status:str
    provenance_refs:tuple[str,...]

def create_recovery_record(*,evidence_id:str,authorization_id:str,attempt_id:str,original_result:str,recovery_state:str,compensation_contract_id:str,compensation_target:str,reason:str,prior_evidence_digest:str,status:str,provenance_refs:tuple[str,...])->CollaborationRecoveryRecord:
    if recovery_state not in RECOVERY: raise ValueError("invalid recovery state")
    if not all(x.strip() for x in (evidence_id,authorization_id,attempt_id,original_result,reason,prior_evidence_digest)): raise ValueError("recovery identity is required")
    if recovery_state in {"COMPENSATION_REQUIRED","COMPENSATED","COMPENSATION_FAILED"} and not compensation_contract_id.strip(): raise ValueError("compensation contract is required")
    if status not in {"RECORDED","BLOCKED"}: raise ValueError("invalid recovery status")
    if not provenance_refs: raise ValueError("recovery provenance is required")
    if recovery_state=="COMPENSATED" and status!="RECORDED": raise ValueError("compensated recovery must be recorded")
    canonical={"evidence_id":evidence_id,"authorization_id":authorization_id,"attempt_id":attempt_id,"original_result":original_result,"recovery_state":recovery_state,"compensation_contract_id":compensation_contract_id,"compensation_target":compensation_target,"reason":reason,"prior_evidence_digest":prior_evidence_digest,"status":status,"provenance_refs":provenance_refs}
    rid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return CollaborationRecoveryRecord(rid,evidence_id,authorization_id,attempt_id,original_result,recovery_state,compensation_contract_id,compensation_target,reason,prior_evidence_digest,status,provenance_refs)

def recovery_preserves_original_evidence(*,record:CollaborationRecoveryRecord,current_evidence_digest:str)->bool:
    return record.prior_evidence_digest==current_evidence_digest and record.status=="RECORDED"

def recovery_allows_learning(*,record:CollaborationRecoveryRecord)->bool:
    return record.recovery_state in {"NO_ACTION","COMPENSATED"} and record.status=="RECORDED"
