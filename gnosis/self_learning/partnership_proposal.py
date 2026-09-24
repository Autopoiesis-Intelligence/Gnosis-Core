"""Evidence-bound partnership proposal generator (E8.12)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class PartnershipProposal:
    proposal_id:str; opportunity_id:str; partner_scope:str; core_scope:str; expected_result:str; constraints:tuple[str,...]; evidence_refs:tuple[str,...]; commercial_decision_id:str; status:str

def generate_partnership_proposal(*,opportunity_id,partner_scope,core_scope,expected_result,constraints,evidence_refs,commercial_decision_id,commercial_eligible,status="PROPOSED"):
    if not all(x.strip() for x in (opportunity_id,partner_scope,core_scope,expected_result,commercial_decision_id)): raise ValueError("complete partnership proposal fields are required")
    if not partner_scope.startswith("partner:"): raise ValueError("partner scope required")
    if not constraints or not evidence_refs: raise ValueError("constraints and evidence are required")
    if not commercial_eligible: raise ValueError("commercial evidence gate must be admitted")
    if status not in {"PROPOSED","REVIEW_REQUIRED","REJECTED"}: raise ValueError("invalid status")
    cs=tuple(sorted(set(constraints))); refs=tuple(sorted(set(evidence_refs)))
    c=dict(opportunity_id=opportunity_id,partner_scope=partner_scope.strip(),core_scope=core_scope.strip(),expected_result=expected_result.strip(),constraints=cs,evidence_refs=refs,commercial_decision_id=commercial_decision_id,status=status)
    pid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return PartnershipProposal(pid,**c)

def may_submit(*,proposal): return proposal.status in {"PROPOSED","REVIEW_REQUIRED"}
def creates_contract(*,proposal): return False
def grants_execution_authority(*,proposal): return False
