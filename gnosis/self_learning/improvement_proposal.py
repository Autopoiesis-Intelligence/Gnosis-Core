"""Auditable self-improvement proposal formation (E8.03)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class ImprovementProposal:
    proposal_id:str; memory_entry_id:str; cycle_id:str; input_id:str; opportunity_id:str; contract_id:str; scope:str; value_level:str; evidence_refs:tuple[str,...]; financial_refs:tuple[str,...]; rationale:str; expected_result:str; acceptance_conditions:tuple[str,...]; unresolved_gaps:tuple[str,...]; status:str

def form_improvement_proposal(*,memory_entry_id,cycle_id,input_id,opportunity_id,contract_id,scope,value_level,evidence_refs,financial_refs=(),rationale,expected_result,acceptance_conditions,unresolved_gaps=(),status="PROPOSED"):
    if not all(x.strip() for x in (memory_entry_id,cycle_id,input_id,opportunity_id,contract_id,scope,rationale,expected_result)): raise ValueError("complete provenance and proposal fields are required")
    if not evidence_refs or not acceptance_conditions: raise ValueError("evidence and acceptance conditions are required")
    if value_level=="COMMERCIAL" and (not financial_refs or not scope.startswith("partner:")): raise ValueError("commercial proposal requires financial evidence and partner scope")
    if status not in {"PROPOSED","ADMITTED","REJECTED","BLOCKED"}: raise ValueError("invalid status")
    refs=tuple(sorted(set(evidence_refs))); fin=tuple(sorted(set(financial_refs))); acc=tuple(sorted(set(acceptance_conditions))); gaps=tuple(sorted(set(unresolved_gaps)))
    c=dict(memory_entry_id=memory_entry_id,cycle_id=cycle_id,input_id=input_id,opportunity_id=opportunity_id,contract_id=contract_id,scope=scope.strip(),value_level=value_level,evidence_refs=refs,financial_refs=fin,rationale=rationale.strip(),expected_result=expected_result.strip(),acceptance_conditions=acc,unresolved_gaps=gaps,status=status)
    pid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":" )).encode()).hexdigest()
    return ImprovementProposal(pid,**c)

def may_review(*,proposal): return proposal.status in {"PROPOSED","ADMITTED"} and bool(proposal.evidence_refs)
def creates_execution_authority(*,proposal): return False
