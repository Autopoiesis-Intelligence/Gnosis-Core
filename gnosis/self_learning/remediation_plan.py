"""Governed remediation plan and compensation authorization (E7.80)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass

PLAN_TYPES={"REMEDIATE","COMPENSATE","CONTAIN","NO_ACTION","MANUAL_REVIEW"}
STATUSES={"PROPOSED","ACCEPTED","REJECTED","BLOCKED"}

@dataclass(frozen=True)
class RemediationPlan:
    plan_id:str
    incident_id:str
    resolution_id:str
    plan_type:str
    target_resource:str
    scope:str
    privacy_classification:str
    rationale:str
    evidence_refs:tuple[str,...]
    preconditions:tuple[str,...]
    authorization_basis:str
    status:str

def create_remediation_plan(*,incident_id:str,resolution_id:str,plan_type:str,target_resource:str,scope:str,privacy_classification:str,rationale:str,evidence_refs:tuple[str,...],preconditions:tuple[str,...],authorization_basis:str,status:str="PROPOSED")->RemediationPlan:
    if plan_type not in PLAN_TYPES: raise ValueError("invalid plan type")
    if status not in STATUSES: raise ValueError("invalid plan status")
    if not all(x.strip() for x in (incident_id,resolution_id,target_resource,scope,privacy_classification,rationale,authorization_basis)): raise ValueError("plan identity is required")
    if not evidence_refs or not preconditions: raise ValueError("evidence and preconditions are required")
    if status=="ACCEPTED" and plan_type=="MANUAL_REVIEW": raise ValueError("manual review cannot be an accepted mutation plan")
    canonical={"incident_id":incident_id,"resolution_id":resolution_id,"plan_type":plan_type,"target_resource":target_resource,"scope":scope,"privacy_classification":privacy_classification,"rationale":rationale,"evidence_refs":evidence_refs,"preconditions":preconditions,"authorization_basis":authorization_basis,"status":status}
    pid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return RemediationPlan(pid,incident_id,resolution_id,plan_type,target_resource,scope,privacy_classification,rationale,evidence_refs,preconditions,authorization_basis,status)

def plan_grants_execution_authority(*,plan:RemediationPlan)->bool:
    return False

def plan_is_admissible(*,plan:RemediationPlan)->bool:
    return plan.status=="ACCEPTED" and plan.plan_type in {"REMEDIATE","COMPENSATE","CONTAIN","NO_ACTION"} and bool(plan.evidence_refs) and bool(plan.preconditions)
