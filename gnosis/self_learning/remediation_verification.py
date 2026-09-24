"""Verified remediation result and governed closure boundary (E7.82)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
STATUSES={"VERIFIED","FAILED","PARTIAL","UNKNOWN","MISMATCH","BLOCKED"}
CLOSURE={"CLOSED","REOPEN_REQUIRED","MANUAL_REVIEW","NOT_CLOSED"}
@dataclass(frozen=True)
class RemediationVerification:
    verification_id:str
    authorization_id:str
    plan_id:str
    incident_id:str
    action:str
    target_resource:str
    authorized_scope:str
    observed_scope:str
    result_status:str
    target_before:str
    target_after:str
    evidence_refs:tuple[str,...]
    verification_basis:str
    closure_state:str
def create_verification(*,authorization_id,plan_id,incident_id,action,target_resource,authorized_scope,observed_scope,result_status,target_before,target_after,evidence_refs,verification_basis,closure_state):
    if result_status not in STATUSES: raise ValueError("invalid verification status")
    if closure_state not in CLOSURE: raise ValueError("invalid closure state")
    if not all(x.strip() for x in (authorization_id,plan_id,incident_id,action,target_resource,authorized_scope,observed_scope,target_before,target_after,verification_basis)): raise ValueError("verification identity is required")
    if not evidence_refs: raise ValueError("verification evidence is required")
    if result_status=="VERIFIED" and closure_state!="CLOSED": raise ValueError("verified result must be closed")
    if result_status!="VERIFIED" and closure_state=="CLOSED": raise ValueError("non-verified result cannot close")
    c={"authorization_id":authorization_id,"plan_id":plan_id,"incident_id":incident_id,"action":action,"target_resource":target_resource,"authorized_scope":authorized_scope,"observed_scope":observed_scope,"result_status":result_status,"target_before":target_before,"target_after":target_after,"evidence_refs":evidence_refs,"verification_basis":verification_basis,"closure_state":closure_state}
    vid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return RemediationVerification(vid,authorization_id,plan_id,incident_id,action,target_resource,authorized_scope,observed_scope,result_status,target_before,target_after,evidence_refs,verification_basis,closure_state)
def closure_is_valid(*,verification):
    return verification.result_status=="VERIFIED" and verification.closure_state=="CLOSED" and verification.authorized_scope==verification.observed_scope
