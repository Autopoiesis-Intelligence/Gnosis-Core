"""Evidence-based dynamic opportunity reclassification (E8.01)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
LEVELS=("LOW_RELEVANCE","RESEARCH_RELEVANT","COMMERCIAL")
@dataclass(frozen=True)
class Reclassification:
    event_id:str; opportunity_id:str; previous_level:str; proposed_level:str; evidence_refs:tuple[str,...]; reason:str; status:str
def propose_reclassification(*,opportunity_id,previous_level,proposed_level,evidence_refs,reason,status="PROPOSED"):
    if not all(x.strip() for x in (opportunity_id,reason)): raise ValueError("reclassification identity is required")
    if previous_level not in LEVELS or proposed_level not in LEVELS: raise ValueError("invalid opportunity level")
    if not evidence_refs: raise ValueError("reclassification requires evidence")
    if status not in {"PROPOSED","ACCEPTED","REJECTED","BLOCKED"}: raise ValueError("invalid status")
    refs=tuple(sorted(set(evidence_refs)))
    c={"opportunity_id":opportunity_id,"previous_level":previous_level,"proposed_level":proposed_level,"evidence_refs":refs,"reason":reason.strip(),"status":status}
    eid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return Reclassification(eid,opportunity_id,previous_level,proposed_level,refs,reason.strip(),status)
def evidence_sufficient(*,event): return bool(event.evidence_refs)
def level_changed(*,event): return event.previous_level!=event.proposed_level
def may_apply(*,event): return event.status=="ACCEPTED" and evidence_sufficient(event=event) and level_changed(event=event)
def creates_execution_authority(*,event): return False
