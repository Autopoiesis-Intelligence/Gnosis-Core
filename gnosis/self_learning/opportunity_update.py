"""Evidence-gated opportunity update from durable learning (E8.10)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
LEVELS=("LOW_RELEVANCE","RESEARCH_RELEVANT","COMMERCIAL")
@dataclass(frozen=True)
class OpportunityUpdate:
    update_id:str; opportunity_id:str; prior_level:str; proposed_level:str; learning_commit_id:str; evidence_refs:tuple[str,...]; rationale:str; status:str

def propose_opportunity_update(*,opportunity_id,prior_level,proposed_level,learning_commit_id,evidence_refs,rationale,status="PROPOSED"):
    if not all(x.strip() for x in (opportunity_id,learning_commit_id,rationale)): raise ValueError("complete opportunity update fields are required")
    if prior_level not in LEVELS or proposed_level not in LEVELS: raise ValueError("invalid value level")
    if not evidence_refs: raise ValueError("opportunity update requires evidence")
    if status not in {"PROPOSED","ADMITTED","REJECTED","BLOCKED"}: raise ValueError("invalid status")
    if proposed_level=="COMMERCIAL" and prior_level!="COMMERCIAL": raise ValueError("promotion to commercial requires dedicated commercial evidence gate")
    refs=tuple(sorted(set(evidence_refs)))
    c=dict(opportunity_id=opportunity_id,prior_level=prior_level,proposed_level=proposed_level,learning_commit_id=learning_commit_id,evidence_refs=refs,rationale=rationale.strip(),status=status)
    uid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return OpportunityUpdate(uid,**c)

def may_apply(*,update,learning_commit_verified): return update.status=="ADMITTED" and learning_commit_verified
def creates_contract(*,update): return False
