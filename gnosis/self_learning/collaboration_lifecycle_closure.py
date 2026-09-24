"""Governed collaboration lifecycle closure and contract retirement (E7.83)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
STATES={"ACTIVE","VERIFIED_CLOSED","REOPENED","RETIRED","BLOCKED"}
REASONS={"VERIFIED_SUCCESS","VERIFIED_FAILURE","COMPENSATED","NO_ACTION","MANUAL_RETIREMENT"}
@dataclass(frozen=True)
class CollaborationLifecycleClosure:
    closure_id:str
    contract_id:str
    incident_id:str
    verification_id:str
    final_state:str
    retirement_reason:str
    evidence_refs:tuple[str,...]
    successor_contract_id:str
    closed_at_evidence:str
    status:str
def create_lifecycle_closure(*,contract_id,incident_id,verification_id,final_state,retirement_reason,evidence_refs,successor_contract_id="",closed_at_evidence,status="RECORDED"):
    if final_state not in STATES: raise ValueError("invalid lifecycle state")
    if retirement_reason not in REASONS: raise ValueError("invalid retirement reason")
    if status not in {"RECORDED","BLOCKED"}: raise ValueError("invalid closure status")
    if not all(x.strip() for x in (contract_id,incident_id,verification_id,closed_at_evidence)): raise ValueError("closure identity is required")
    if not evidence_refs: raise ValueError("closure evidence is required")
    if final_state=="VERIFIED_CLOSED" and retirement_reason=="MANUAL_RETIREMENT": raise ValueError("verified closure cannot be represented as manual retirement")
    c={"contract_id":contract_id,"incident_id":incident_id,"verification_id":verification_id,"final_state":final_state,"retirement_reason":retirement_reason,"evidence_refs":evidence_refs,"successor_contract_id":successor_contract_id,"closed_at_evidence":closed_at_evidence,"status":status}
    cid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return CollaborationLifecycleClosure(cid,contract_id,incident_id,verification_id,final_state,retirement_reason,evidence_refs,successor_contract_id,closed_at_evidence,status)
def retirement_is_valid(*,closure):
    return closure.status=="RECORDED" and closure.final_state in {"VERIFIED_CLOSED","RETIRED"} and bool(closure.evidence_refs)
def closure_creates_authority(*,closure): return False
