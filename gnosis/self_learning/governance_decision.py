"""Deterministic governance decision boundary for self-learning proposals (E7.94)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class GovernanceDecision:
    decision_id:str; proposal_id:str; proposal_base_state_digest:str; current_state_digest:str; evidence_refs:tuple[str,...]; required_approvals:int; approvals:int; decision_revision:str; outcome:str
def decide(*,proposal_id,proposal_base_state_digest,current_state_digest,evidence_refs,required_approvals,approvals,decision_revision="r1",outcome="PENDING"):
    if not all(x.strip() for x in (proposal_id,proposal_base_state_digest,current_state_digest,decision_revision)): raise ValueError("decision identity is required")
    if not evidence_refs: raise ValueError("decision evidence is required")
    if required_approvals < 1 or approvals < 0: raise ValueError("invalid approval counts")
    if outcome not in {"PENDING","APPROVED","REJECTED","BLOCKED","STALE"}: raise ValueError("invalid outcome")
    refs=tuple(sorted(set(evidence_refs)))
    c={"proposal_id":proposal_id,"proposal_base_state_digest":proposal_base_state_digest,"current_state_digest":current_state_digest,"evidence_refs":refs,"required_approvals":required_approvals,"approvals":approvals,"decision_revision":decision_revision,"outcome":outcome}
    did="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return GovernanceDecision(did,proposal_id,proposal_base_state_digest,current_state_digest,refs,required_approvals,approvals,decision_revision,outcome)
def may_commit(*,decision):
    return decision.outcome=="APPROVED" and decision.approvals>=decision.required_approvals and decision.proposal_base_state_digest==decision.current_state_digest and bool(decision.evidence_refs)
def is_stale(*,decision): return decision.proposal_base_state_digest!=decision.current_state_digest
def creates_execution_authority(*,decision): return False
