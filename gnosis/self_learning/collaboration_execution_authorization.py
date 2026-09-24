"""Fail-closed authorization record for external collaboration actions (E7.76)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass

ACTIONS={"PUBLISH_PUBLIC","CREATE_PUBLIC_ISSUE_PR","DELIVER_PARTNER_PACKAGE","SEND_INVITATION","UPDATE_PUBLIC_METADATA"}

@dataclass(frozen=True)
class CollaborationExecutionAuthorization:
    authorization_id:str
    review_id:str
    proposal_id:str
    proposal_revision:str
    action:str
    target_resource:str
    authorized_scope:str
    executor_id:str
    authorization_basis:str
    privacy_classification:str
    issuance_revision:str
    expiry_evidence:str
    revocation_state:str
    preconditions:tuple[str,...]
    status:str

def issue_authorization(*,review_id:str,proposal_id:str,proposal_revision:str,review_decision:str,action:str,target_resource:str,authorized_scope:str,executor_id:str,authorization_basis:str,privacy_classification:str,issuance_revision:str,expiry_evidence:str,revocation_state:str,preconditions:tuple[str,...],status:str="AUTHORIZED")->CollaborationExecutionAuthorization:
    if review_decision!="ACCEPTED": raise ValueError("authorization requires ACCEPTED review")
    if action not in ACTIONS: raise ValueError("unknown action")
    if not all(x.strip() for x in (review_id,proposal_id,proposal_revision,target_resource,authorized_scope,executor_id,authorization_basis,privacy_classification,issuance_revision,expiry_evidence)): raise ValueError("authorization identity is required")
    if revocation_state!="ACTIVE": raise ValueError("authorization must be active")
    if not preconditions: raise ValueError("preconditions are required")
    if status!="AUTHORIZED": raise ValueError("invalid authorization status")
    canonical={"review_id":review_id,"proposal_id":proposal_id,"proposal_revision":proposal_revision,"action":action,"target_resource":target_resource,"authorized_scope":authorized_scope,"executor_id":executor_id,"authorization_basis":authorization_basis,"privacy_classification":privacy_classification,"issuance_revision":issuance_revision,"expiry_evidence":expiry_evidence,"revocation_state":revocation_state,"preconditions":preconditions,"status":status}
    aid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return CollaborationExecutionAuthorization(aid,review_id,proposal_id,proposal_revision,action,target_resource,authorized_scope,executor_id,authorization_basis,privacy_classification,issuance_revision,expiry_evidence,revocation_state,preconditions,status)

def authorization_valid(*,authorization:CollaborationExecutionAuthorization,review_id:str,proposal_revision:str,action:str,target_resource:str,scope:str,privacy_classification:str,revoked:bool=False,expired:bool=False,stale:bool=False)->bool:
    return (authorization.status=="AUTHORIZED" and authorization.review_id==review_id and authorization.proposal_revision==proposal_revision and authorization.action==action and authorization.target_resource==target_resource and authorization.authorized_scope==scope and authorization.privacy_classification==privacy_classification and authorization.revocation_state=="ACTIVE" and not revoked and not expired and not stale)
