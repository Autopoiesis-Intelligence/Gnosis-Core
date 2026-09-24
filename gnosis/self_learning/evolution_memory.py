"""Verified Evolution Memory admission boundary (E7.97)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class EvolutionMemoryEntry:
    entry_id:str; verification_id:str; commit_id:str; verified_state_digest:str; evidence_refs:tuple[str,...]; learning_scope:str; entry_revision:str; status:str
def admit_verified(*,verification_id,commit_id,verified_state_digest,evidence_refs,learning_scope,entry_revision="r1",status="PROPOSED",verification_outcome="VERIFIED",observed_state_digest=None):
    if not all(x.strip() for x in (verification_id,commit_id,verified_state_digest,learning_scope,entry_revision)): raise ValueError("memory identity is required")
    if not evidence_refs: raise ValueError("memory evidence is required")
    if status not in {"PROPOSED","ADMITTED","REJECTED","BLOCKED"}: raise ValueError("invalid status")
    if verification_outcome!="VERIFIED" or observed_state_digest!=verified_state_digest: raise ValueError("only exact verified state may enter memory")
    refs=tuple(sorted(set(evidence_refs)))
    c={"verification_id":verification_id,"commit_id":commit_id,"verified_state_digest":verified_state_digest,"evidence_refs":refs,"learning_scope":learning_scope.strip(),"entry_revision":entry_revision,"status":status}
    eid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return EvolutionMemoryEntry(eid,verification_id,commit_id,verified_state_digest,refs,learning_scope.strip(),entry_revision,status)
def may_enter_next_cycle(*,entry): return entry.status=="ADMITTED" and bool(entry.evidence_refs)
def creates_execution_authority(*,entry): return False
