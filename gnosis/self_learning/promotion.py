"""Governed gate for proposing knowledge promotion to common Core learning."""
from __future__ import annotations
import hashlib, json
from dataclasses import dataclass
from .lineage import KnowledgeVersion

@dataclass(frozen=True)
class PromotionProposal:
    proposal_id: str
    version_id: str
    subject_id: str
    target: str
    evidence_refs: tuple[str, ...]
    reason: str
    status: str = "PROPOSED"
    authority: str = "promotion-proposal-only"

def propose_promotion(version: KnowledgeVersion, *, evidence_refs: tuple[str,...], reason: str, target: str="common-self-learning") -> PromotionProposal:
    if version.status != "RECORDED":
        raise ValueError("only recorded knowledge versions may be proposed")
    if not evidence_refs or any(not x.strip() for x in evidence_refs):
        raise ValueError("promotion requires evidence references")
    if not reason.strip() or not target.strip():
        raise ValueError("reason and target must be non-empty")
    canonical={"version_id":version.version_id,"subject_id":version.subject_id,"target":target,"evidence_refs":evidence_refs,"reason":reason}
    pid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return PromotionProposal(pid,version.version_id,version.subject_id,target,evidence_refs,reason)

def decide_promotion(proposal: PromotionProposal, *, decision: str, reviewer: str) -> PromotionProposal:
    if proposal.status != "PROPOSED":
        raise ValueError("only PROPOSED promotion proposals may be decided")
    if decision not in {"ACCEPTED","REJECTED","DEFERRED"}:
        raise ValueError("invalid promotion decision")
    if not reviewer.strip():
        raise ValueError("reviewer is required")
    return PromotionProposal(proposal.proposal_id,proposal.version_id,proposal.subject_id,proposal.target,proposal.evidence_refs,proposal.reason,decision,proposal.authority)
