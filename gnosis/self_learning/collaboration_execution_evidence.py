"""Execution evidence and reconciliation for authorized collaboration actions (E7.77)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass

RESULTS={"NOT_ATTEMPTED","ATTEMPTED","SUCCEEDED","FAILED","PARTIAL","UNKNOWN","REJECTED_BY_BOUNDARY"}
RECON={"RECONCILED","MISMATCH","INCOMPLETE","UNKNOWN","REJECTED"}

@dataclass(frozen=True)
class ExecutionEvidence:
    evidence_id:str
    authorization_id:str
    review_id:str
    proposal_revision:str
    action:str
    target_resource:str
    authorized_scope:str
    executor_id:str
    attempt_id:str
    ordering_evidence:str
    result_status:str
    target_before:str
    target_after:str
    privacy_classification:str
    reconciliation_status:str
    provenance_refs:tuple[str,...]
    evidence_digest:str

def create_execution_evidence(*,authorization_id:str,review_id:str,proposal_revision:str,action:str,target_resource:str,authorized_scope:str,executor_id:str,attempt_id:str,ordering_evidence:str,result_status:str,target_before:str,target_after:str,privacy_classification:str,reconciliation_status:str,provenance_refs:tuple[str,...])->ExecutionEvidence:
    if result_status not in RESULTS or reconciliation_status not in RECON: raise ValueError("invalid execution/reconciliation state")
    fields=(authorization_id,review_id,proposal_revision,action,target_resource,authorized_scope,executor_id,attempt_id,ordering_evidence,privacy_classification)
    if any(not x.strip() for x in fields): raise ValueError("execution identity is required")
    if not provenance_refs: raise ValueError("provenance is required")
    if result_status in {"UNKNOWN","FAILED","PARTIAL","REJECTED_BY_BOUNDARY"} and reconciliation_status=="RECONCILED": raise ValueError("non-success result cannot be reconciled")
    canonical={"authorization_id":authorization_id,"review_id":review_id,"proposal_revision":proposal_revision,"action":action,"target_resource":target_resource,"authorized_scope":authorized_scope,"executor_id":executor_id,"attempt_id":attempt_id,"ordering_evidence":ordering_evidence,"result_status":result_status,"target_before":target_before,"target_after":target_after,"privacy_classification":privacy_classification,"reconciliation_status":reconciliation_status,"provenance_refs":provenance_refs}
    eid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    digest="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return ExecutionEvidence(eid,authorization_id,review_id,proposal_revision,action,target_resource,authorized_scope,executor_id,attempt_id,ordering_evidence,result_status,target_before,target_after,privacy_classification,reconciliation_status,provenance_refs,digest)

def reconciled(*,evidence:ExecutionEvidence,authorization_id:str,action:str,target_resource:str,scope:str,privacy_classification:str)->bool:
    return evidence.reconciliation_status=="RECONCILED" and evidence.authorization_id==authorization_id and evidence.action==action and evidence.target_resource==target_resource and evidence.authorized_scope==scope and evidence.privacy_classification==privacy_classification and evidence.result_status=="SUCCEEDED"
