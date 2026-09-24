"""Opportunity value grid for self-learning contract routing (E8.00)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
LEVELS=("LOW_RELEVANCE","RESEARCH_RELEVANT","COMMERCIAL")
@dataclass(frozen=True)
class Opportunity:
    opportunity_id:str; source_refs:tuple[str,...]; evidence_refs:tuple[str,...]; value_level:str; scope:str; rationale:str; contract_kind:str; status:str
def classify_opportunity(*,source_refs,evidence_refs,value_level,scope,rationale,contract_kind="DEVELOPMENT",status="PROPOSED"):
    if not source_refs or not evidence_refs: raise ValueError("opportunity requires source and evidence references")
    if value_level not in LEVELS: raise ValueError("invalid value level")
    if not all(x.strip() for x in (scope,rationale,contract_kind)): raise ValueError("classification fields are required")
    if status not in {"PROPOSED","ADMITTED","REJECTED","BLOCKED"}: raise ValueError("invalid status")
    c={"source_refs":tuple(sorted(set(source_refs))),"evidence_refs":tuple(sorted(set(evidence_refs))),"value_level":value_level,"scope":scope.strip(),"rationale":rationale.strip(),"contract_kind":contract_kind.strip(),"status":status}
    oid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return Opportunity(oid,c["source_refs"],c["evidence_refs"],value_level,c["scope"],c["rationale"],c["contract_kind"],status)
def route_opportunity(*,opportunity):
    return {"LOW_RELEVANCE":"GENERAL_BACKLOG","RESEARCH_RELEVANT":"RESEARCH_CONTRACT","COMMERCIAL":"PARTNER_CONTRACT"}[opportunity.value_level]
def may_form_contract(*,opportunity): return opportunity.status=="ADMITTED"
def is_partner_isolated(*,opportunity): return opportunity.value_level!="COMMERCIAL" or opportunity.scope.startswith("partner:")
