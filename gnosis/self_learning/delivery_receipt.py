"""Receipt proving authorized delivery of a specialized Core."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass

@dataclass(frozen=True)
class PartnerDeliveryReceipt:
    receipt_id:str
    authorization_id:str
    delivery_manifest_id:str
    core_build_revision:str
    partner_id:str
    knowledge_scope:str
    delivered_revision:str
    evidence_refs:tuple[str,...]
    status:str="RECORDED"

def create_delivery_receipt(*,authorization_id:str,delivery_manifest_id:str,core_build_revision:str,partner_id:str,knowledge_scope:str,delivered_revision:str,evidence_refs:tuple[str,...],status:str="RECORDED")->PartnerDeliveryReceipt:
    if not all(x.strip() for x in (authorization_id,delivery_manifest_id,core_build_revision,partner_id,knowledge_scope,delivered_revision)):
        raise ValueError("delivery receipt identity fields are required")
    if not evidence_refs: raise ValueError("delivery evidence is required")
    if status not in {"RECORDED","REJECTED"}: raise ValueError("invalid delivery status")
    canonical={"authorization_id":authorization_id,"delivery_manifest_id":delivery_manifest_id,"core_build_revision":core_build_revision,"partner_id":partner_id,"knowledge_scope":knowledge_scope,"delivered_revision":delivered_revision,"evidence_refs":evidence_refs,"status":status}
    rid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return PartnerDeliveryReceipt(rid,authorization_id,delivery_manifest_id,core_build_revision,partner_id,knowledge_scope,delivered_revision,evidence_refs,status)

def delivery_receipt_valid(*,authorization_status:str,release_decision:str,receipt:PartnerDeliveryReceipt)->bool:
    return authorization_status=="AUTHORIZED" and release_decision=="RELEASE" and receipt.status=="RECORDED" and bool(receipt.evidence_refs)
