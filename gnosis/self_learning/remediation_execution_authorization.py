"""Controlled remediation execution authorization boundary (E7.81)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
ACTIONS={"REMEDIATE","COMPENSATE","CONTAIN","NO_ACTION"}
STATUSES={"PROPOSED","AUTHORIZED","REVOKED","EXPIRED","BLOCKED"}
@dataclass(frozen=True)
class RemediationExecutionAuthorization:
    authorization_id:str; plan_id:str; incident_id:str; action:str; target_resource:str; scope:str; privacy_classification:str; preconditions:tuple[str,...]; evidence_refs:tuple[str,...]; authorization_basis:str; status:str
def create_authorization(*,plan_id,incident_id,action,target_resource,scope,privacy_classification,preconditions,evidence_refs,authorization_basis,status="PROPOSED"):
    if action not in ACTIONS: raise ValueError("invalid remediation action")
    if status not in STATUSES: raise ValueError("invalid authorization status")
    if not all(x.strip() for x in (plan_id,incident_id,target_resource,scope,privacy_classification,authorization_basis)): raise ValueError("authorization identity is required")
    if not preconditions or not evidence_refs: raise ValueError("preconditions and evidence are required")
    c={"plan_id":plan_id,"incident_id":incident_id,"action":action,"target_resource":target_resource,"scope":scope,"privacy_classification":privacy_classification,"preconditions":preconditions,"evidence_refs":evidence_refs,"authorization_basis":authorization_basis,"status":status}
    aid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return RemediationExecutionAuthorization(aid,plan_id,incident_id,action,target_resource,scope,privacy_classification,preconditions,evidence_refs,authorization_basis,status)
def may_execute(*,authorization): return authorization.status=="AUTHORIZED" and bool(authorization.preconditions) and bool(authorization.evidence_refs)
def authorization_matches_plan(*,authorization,plan_id,incident_id,action,target_resource,scope,privacy_classification):
    return (authorization.plan_id==plan_id and authorization.incident_id==incident_id and authorization.action==action and authorization.target_resource==target_resource and authorization.scope==scope and authorization.privacy_classification==privacy_classification)
