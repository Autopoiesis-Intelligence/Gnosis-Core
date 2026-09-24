"""Learning-cycle re-entry and provenance continuity boundary (E7.98)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class LearningCycle:
    cycle_id:str; parent_memory_entry_id:str; parent_state_digest:str; input_refs:tuple[str,...]; scope:str; cycle_revision:str; status:str
def start_cycle(*,parent_memory_entry_id,parent_state_digest,input_refs,scope,cycle_revision="r1",status="STARTED",memory_status="ADMITTED"):
    if not all(x.strip() for x in (parent_memory_entry_id,parent_state_digest,scope,cycle_revision)): raise ValueError("cycle identity is required")
    if not input_refs: raise ValueError("cycle requires input references")
    if memory_status!="ADMITTED": raise ValueError("only admitted memory may start a cycle")
    if status not in {"STARTED","ACTIVE","COMPLETED","BLOCKED"}: raise ValueError("invalid cycle status")
    refs=tuple(sorted(set(input_refs)))
    c={"parent_memory_entry_id":parent_memory_entry_id,"parent_state_digest":parent_state_digest,"input_refs":refs,"scope":scope.strip(),"cycle_revision":cycle_revision,"status":status}
    cid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return LearningCycle(cid,parent_memory_entry_id,parent_state_digest,refs,scope.strip(),cycle_revision,status)
def provenance_continuous(*,cycle,parent_memory_entry_id,parent_state_digest): return cycle.parent_memory_entry_id==parent_memory_entry_id and cycle.parent_state_digest==parent_state_digest and bool(cycle.input_refs)
def may_extract(*,cycle): return cycle.status in {"STARTED","ACTIVE"} and bool(cycle.input_refs)
def creates_execution_authority(*,cycle): return False
