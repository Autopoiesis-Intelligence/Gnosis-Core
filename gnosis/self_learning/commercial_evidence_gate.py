"""Dedicated commercial evidence gate (E8.11)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class CommercialEvidenceDecision:
    decision_id:str; opportunity_id:str; evidence_refs:tuple[str,...]; financial_refs:tuple[str,...]; partner_scope:str; decision:str; rationale:str; status:str

def assess_commercial_evidence(*,opportunity_id,evidence_refs,financial_refs,partner_scope,rationale,status="PROPOSED"):
    if not all(x.strip() for x in (opportunity_id,partner_scope,rationale)): raise ValueError("complete commercial assessment fields are required")
    if not partner_scope.startswith("partner:"): raise ValueError("commercial assessment requires partner scope")
    if not evidence_refs or not financial_refs: raise ValueError("commercial assessment requires evidence and financial evidence")
    if status not in {"PROPOSED","ADMITTED","REJECTED","BLOCKED"}: raise ValueError("invalid status")
    refs=tuple(sorted(set(evidence_refs))); fin=tuple(sorted(set(financial_refs)))
    c=dict(opportunity_id=opportunity_id,evidence_refs=refs,financial_refs=fin,partner_scope=partner_scope.strip(),decision="COMMERCIAL_ELIGIBLE",rationale=rationale.strip(),status=status)
    did="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return CommercialEvidenceDecision(did,**c)

def may_promote(*,decision): return decision.status=="ADMITTED" and decision.decision=="COMMERCIAL_ELIGIBLE"
def creates_contract(*,decision): return False
