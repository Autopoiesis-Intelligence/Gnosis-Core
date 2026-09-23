"""Final authorization binding a released specialized Core to its delivery manifest."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass

@dataclass(frozen=True)
class DeliveryAuthorization:
    authorization_id:str
    release_gate_id:str
    build_record_id:str
    delivery_manifest_id:str
    partner_id:str
    knowledge_scope:str
    authorization_revision:str
    status:str="HOLD"

def create_delivery_authorization(*,release_gate_id:str,build_record_id:str,delivery_manifest_id:str,partner_id:str,knowledge_scope:str,authorization_revision:str,status:str="HOLD")->DeliveryAuthorization:
    if not all(x.strip() for x in (release_gate_id,build_record_id,delivery_manifest_id,partner_id,knowledge_scope,authorization_revision)):
        raise ValueError("authorization identity fields are required")
    if status not in {"HOLD","AUTHORIZED","REVOKED"}: raise ValueError("invalid authorization status")
    canonical={"release_gate_id":release_gate_id,"build_record_id":build_record_id,"delivery_manifest_id":delivery_manifest_id,"partner_id":partner_id,"knowledge_scope":knowledge_scope,"authorization_revision":authorization_revision,"status":status}
    aid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return DeliveryAuthorization(aid,release_gate_id,build_record_id,delivery_manifest_id,partner_id,knowledge_scope,authorization_revision,status)

def delivery_authorized(*,release_decision:str,build_status:str,manifest_status:str,authorization:DeliveryAuthorization)->bool:
    return release_decision=="RELEASE" and build_status=="BUILT" and manifest_status=="PROPOSED" and authorization.status=="AUTHORIZED"
