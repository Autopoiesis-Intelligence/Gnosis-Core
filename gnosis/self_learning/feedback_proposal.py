"""Governed post-delivery learning feedback proposal."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass

@dataclass(frozen=True)
class PartnerFeedbackProposal:
    proposal_id:str
    delivery_receipt_id:str
    partner_id:str
    source_scope:str
    artifact_refs:tuple[str,...]
    privacy_filters:tuple[str,...]
    generalizable_findings:tuple[str,...]
    exclusion_refs:tuple[str,...]
    revision:str
    status:str="PROPOSED"

def create_feedback_proposal(*,delivery_receipt_id:str,partner_id:str,source_scope:str,artifact_refs:tuple[str,...],privacy_filters:tuple[str,...],generalizable_findings:tuple[str,...],exclusion_refs:tuple[str,...],revision:str)->PartnerFeedbackProposal:
    if not all(x.strip() for x in (delivery_receipt_id,partner_id,source_scope,revision)): raise ValueError("feedback identity fields are required")
    if not artifact_refs or not privacy_filters or not generalizable_findings or not exclusion_refs: raise ValueError("feedback evidence and boundary groups are required")
    canonical={"delivery_receipt_id":delivery_receipt_id,"partner_id":partner_id,"source_scope":source_scope,"artifact_refs":artifact_refs,"privacy_filters":privacy_filters,"generalizable_findings":generalizable_findings,"exclusion_refs":exclusion_refs,"revision":revision}
    pid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return PartnerFeedbackProposal(pid,delivery_receipt_id,partner_id,source_scope,artifact_refs,privacy_filters,generalizable_findings,exclusion_refs,revision)

def promotion_eligible(*,receipt_valid:bool,privacy_valid:bool,proposal:PartnerFeedbackProposal)->bool:
    return receipt_valid and privacy_valid and proposal.status=="PROPOSED" and bool(proposal.generalizable_findings) and bool(proposal.exclusion_refs)


def validate_feedback_proposal_binding(
    proposal: PartnerFeedbackProposal,
    *,
    expected_delivery_receipt_id: str,
    expected_partner_id: str,
    expected_source_scope: str,
) -> PartnerFeedbackProposal:
    canonical={"delivery_receipt_id":proposal.delivery_receipt_id,"partner_id":proposal.partner_id,"source_scope":proposal.source_scope,"artifact_refs":proposal.artifact_refs,"privacy_filters":proposal.privacy_filters,"generalizable_findings":proposal.generalizable_findings,"exclusion_refs":proposal.exclusion_refs,"revision":proposal.revision}
    expected_id="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if proposal.proposal_id != expected_id:
        raise ValueError("feedback proposal identity does not match immutable fields")
    if (proposal.delivery_receipt_id,proposal.partner_id,proposal.source_scope) != (expected_delivery_receipt_id,expected_partner_id,expected_source_scope):
        raise PermissionError("feedback proposal binding mismatch")
    return proposal
