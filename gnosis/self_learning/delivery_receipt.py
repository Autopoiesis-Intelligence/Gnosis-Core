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


def validate_delivery_receipt_binding(
    receipt: PartnerDeliveryReceipt,
    *,
    expected_authorization_id: str,
    expected_delivery_manifest_id: str,
    expected_core_build_revision: str,
    expected_partner_id: str,
    expected_knowledge_scope: str,
) -> PartnerDeliveryReceipt:
    canonical={"authorization_id":receipt.authorization_id,"delivery_manifest_id":receipt.delivery_manifest_id,"core_build_revision":receipt.core_build_revision,"partner_id":receipt.partner_id,"knowledge_scope":receipt.knowledge_scope,"delivered_revision":receipt.delivered_revision,"evidence_refs":receipt.evidence_refs,"status":receipt.status}
    expected_id="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if receipt.receipt_id != expected_id:
        raise ValueError("delivery receipt identity does not match immutable fields")
    expected=(expected_authorization_id,expected_delivery_manifest_id,expected_core_build_revision,expected_partner_id,expected_knowledge_scope)
    actual=(receipt.authorization_id,receipt.delivery_manifest_id,receipt.core_build_revision,receipt.partner_id,receipt.knowledge_scope)
    if actual != expected:
        raise PermissionError("delivery receipt binding mismatch")
    return receipt
