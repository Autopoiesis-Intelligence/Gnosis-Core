"""Learning input provenance and evidence isolation boundary (E7.99)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class LearningInput:
    input_id:str; cycle_id:str; source_ref:str; evidence_refs:tuple[str,...]; scope:str; confidentiality:str; provenance_digest:str; status:str
def create_learning_input(*,cycle_id,source_ref,evidence_refs,scope,confidentiality="GENERAL",status="ADMITTED"):
    if not all(x.strip() for x in (cycle_id,source_ref,scope)): raise ValueError("input identity is required")
    if not evidence_refs: raise ValueError("input requires evidence references")
    if confidentiality not in {"GENERAL","CORE_PRIVATE","PARTNER_PRIVATE"}: raise ValueError("invalid confidentiality")
    if status not in {"PROPOSED","ADMITTED","REJECTED","BLOCKED"}: raise ValueError("invalid status")
    refs=tuple(sorted(set(evidence_refs)))
    c={"cycle_id":cycle_id,"source_ref":source_ref,"evidence_refs":refs,"scope":scope.strip(),"confidentiality":confidentiality,"status":status}
    digest="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return LearningInput("sha256:"+hashlib.sha256((digest+":id").encode()).hexdigest(),cycle_id,source_ref,refs,scope.strip(),confidentiality,digest,status)
def may_enter_learning(*,item): return item.status=="ADMITTED" and bool(item.evidence_refs)
def may_cross_scope(*,item,target_scope): return item.scope==target_scope and item.confidentiality!="PARTNER_PRIVATE"
def preserves_isolation(*,item,target_scope): return not(item.confidentiality=="PARTNER_PRIVATE" and item.scope!=target_scope)
