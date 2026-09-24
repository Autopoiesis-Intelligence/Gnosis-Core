"""Governed external collaboration incident/conflict resolution (E7.79)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass

STATES={"OPEN","CONFLICT","UNKNOWN","SCOPE_MISMATCH","RESOLVED","UNRESOLVED","CLOSED"}
RESOLUTIONS={"CONFIRMED_SUCCESS","CONFIRMED_FAILURE","CONFIRMED_UNKNOWN","SCOPE_MISMATCH_CONFIRMED","EVIDENCE_CONFLICT","MANUAL_DEFERRED"}

@dataclass(frozen=True)
class CollaborationIncidentResolution:
    resolution_id:str
    incident_id:str
    evidence_refs:tuple[str,...]
    conflicting_evidence_refs:tuple[str,...]
    original_scope:str
    observed_scope:str
    incident_state:str
    resolution:str
    rationale:str
    resolver_id:str
    resolution_revision:str
    authorization_ref:str
    remediation_ref:str
    status:str="RECORDED"

def create_incident_resolution(*,incident_id:str,evidence_refs:tuple[str,...],conflicting_evidence_refs:tuple[str,...],original_scope:str,observed_scope:str,incident_state:str,resolution:str,rationale:str,resolver_id:str,resolution_revision:str,authorization_ref:str="",remediation_ref:str="",status:str="RECORDED")->CollaborationIncidentResolution:
    if incident_state not in STATES: raise ValueError("invalid incident state")
    if resolution not in RESOLUTIONS: raise ValueError("invalid resolution")
    if not all(x.strip() for x in (incident_id,original_scope,observed_scope,rationale,resolver_id,resolution_revision)): raise ValueError("resolution identity is required")
    if not evidence_refs: raise ValueError("source evidence is required")
    if incident_state=="CONFLICT" and not conflicting_evidence_refs: raise ValueError("conflict evidence is required")
    if resolution=="EVIDENCE_CONFLICT" and not conflicting_evidence_refs: raise ValueError("evidence conflict requires conflicting refs")
    if status not in {"RECORDED","BLOCKED"}: raise ValueError("invalid status")
    canonical={"incident_id":incident_id,"evidence_refs":evidence_refs,"conflicting_evidence_refs":conflicting_evidence_refs,"original_scope":original_scope,"observed_scope":observed_scope,"incident_state":incident_state,"resolution":resolution,"rationale":rationale,"resolver_id":resolver_id,"resolution_revision":resolution_revision,"authorization_ref":authorization_ref,"remediation_ref":remediation_ref,"status":status}
    rid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return CollaborationIncidentResolution(rid,incident_id,evidence_refs,conflicting_evidence_refs,original_scope,observed_scope,incident_state,resolution,rationale,resolver_id,resolution_revision,authorization_ref,remediation_ref,status)

def resolution_is_learning_safe(*,record:CollaborationIncidentResolution)->bool:
    return record.status=="RECORDED" and record.resolution in {"CONFIRMED_SUCCESS","CONFIRMED_FAILURE","CONFIRMED_UNKNOWN","SCOPE_MISMATCH_CONFIRMED"} and bool(record.evidence_refs)

def resolution_grants_authority(*,record:CollaborationIncidentResolution)->bool:
    return False
