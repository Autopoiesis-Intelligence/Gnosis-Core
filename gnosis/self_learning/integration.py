"""Controlled integration records for accepted Self-Learning promotions."""
from __future__ import annotations
import hashlib, json
from dataclasses import dataclass
from .promotion import PromotionProposal

@dataclass(frozen=True)
class IntegrationRecord:
    integration_id: str
    proposal_id: str
    version_id: str
    target: str
    action: str
    status: str = "PROPOSED"
    authority: str = "integration-record-only"
    receipt_id: str | None = None

def create_integration_record(proposal: PromotionProposal, *, action: str) -> IntegrationRecord:
    if proposal.status != "ACCEPTED":
        raise ValueError("only ACCEPTED promotion proposals may create integration records")
    if not action.strip():
        raise ValueError("action is required")
    canonical={"proposal_id":proposal.proposal_id,"version_id":proposal.version_id,"target":proposal.target,"action":action}
    iid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return IntegrationRecord(iid,proposal.proposal_id,proposal.version_id,proposal.target,action)

def mark_executed(record: IntegrationRecord, *, receipt_id: str) -> IntegrationRecord:
    if record.status != "PROPOSED":
        raise ValueError("only PROPOSED integration records may be marked executed")
    if not receipt_id.strip():
        raise ValueError("receipt_id is required")
    canonical={"proposal_id":record.proposal_id,"version_id":record.version_id,"target":record.target,"action":record.action}
    expected="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if record.integration_id != expected:
        raise ValueError("integration identity does not match immutable integration fields")
    return IntegrationRecord(record.integration_id,record.proposal_id,record.version_id,record.target,record.action,"EXECUTED",record.authority,receipt_id)
