"""Evidence-gated contract formation and routing (E8.02)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
KINDS={"LOW_RELEVANCE":"GENERAL_OPEN","RESEARCH_RELEVANT":"RESEARCH_LEGAL","COMMERCIAL":"COMMERCIAL_PARTNER"}
@dataclass(frozen=True)
class ContractCandidate:
    contract_id:str; opportunity_id:str; value_level:str; contract_kind:str; scope:str; evidence_refs:tuple[str,...]; financial_refs:tuple[str,...]; status:str
def form_contract_candidate(*,opportunity_id,value_level,scope,evidence_refs,financial_refs=(),status="PROPOSED"):
    if not all(x.strip() for x in (opportunity_id,scope)): raise ValueError("contract identity is required")
    if value_level not in KINDS: raise ValueError("invalid value level")
    if not evidence_refs: raise ValueError("contract requires evidence")
    if status not in {"PROPOSED","ADMITTED","REJECTED","BLOCKED"}: raise ValueError("invalid status")
    fin=tuple(sorted(set(financial_refs))); refs=tuple(sorted(set(evidence_refs)))
    if value_level=="COMMERCIAL" and not fin: raise ValueError("commercial contract requires financial evidence")
    if value_level!="COMMERCIAL" and fin: raise ValueError("financial evidence cannot silently upgrade non-commercial contract")
    c={"opportunity_id":opportunity_id,"value_level":value_level,"contract_kind":KINDS[value_level],"scope":scope.strip(),"evidence_refs":refs,"financial_refs":fin,"status":status}
    cid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return ContractCandidate(cid,opportunity_id,value_level,KINDS[value_level],scope.strip(),refs,fin,status)
def may_issue(*,candidate): return candidate.status=="ADMITTED" and bool(candidate.evidence_refs)
def commercial_route_valid(*,candidate): return candidate.value_level!="COMMERCIAL" or (candidate.scope.startswith("partner:") and bool(candidate.financial_refs))
def creates_execution_authority(*,candidate): return False
