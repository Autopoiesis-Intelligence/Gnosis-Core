"""Immutable record of a governed partner-feedback promotion decision."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass

@dataclass(frozen=True)
class FeedbackPromotionRecord:
    record_id:str
    validation_id:str
    proposal_id:str
    source_delivery_receipt_id:str
    target_knowledge_revision:str
    promoted_finding_refs:tuple[str,...]
    excluded_refs:tuple[str,...]
    decision:str
    record_revision:str

def create_promotion_record(*,validation_id:str,proposal_id:str,source_delivery_receipt_id:str,target_knowledge_revision:str,promoted_finding_refs:tuple[str,...],excluded_refs:tuple[str,...],decision:str,record_revision:str)->FeedbackPromotionRecord:
    if not all(x.strip() for x in (validation_id,proposal_id,source_delivery_receipt_id,target_knowledge_revision,record_revision)): raise ValueError("promotion identity is required")
    if not promoted_finding_refs or not excluded_refs: raise ValueError("promotion and exclusion evidence are required")
    if decision not in {"PROMOTED","REJECTED"}: raise ValueError("invalid promotion decision")
    canonical={"validation_id":validation_id,"proposal_id":proposal_id,"source_delivery_receipt_id":source_delivery_receipt_id,"target_knowledge_revision":target_knowledge_revision,"promoted_finding_refs":promoted_finding_refs,"excluded_refs":excluded_refs,"decision":decision,"record_revision":record_revision}
    rid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return FeedbackPromotionRecord(rid,validation_id,proposal_id,source_delivery_receipt_id,target_knowledge_revision,promoted_finding_refs,excluded_refs,decision,record_revision)

def promotion_record_valid(*,validation_decision:str,record:FeedbackPromotionRecord)->bool:
    return validation_decision=="PROMOTE" and record.decision=="PROMOTED" and bool(record.promoted_finding_refs) and bool(record.excluded_refs)
