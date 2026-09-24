"""Deterministic pattern and relation extraction boundary (E7.90)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class ExtractedPattern:
    extraction_id:str; normalization_id:str; input_digest:str; patterns:tuple[str,...]; relations:tuple[tuple[str,str,str],...]; extraction_revision:str; status:str
def extract_patterns(*,normalization_id,input_digest,facts,extraction_revision="r1",status="PROPOSED"):
    if not all(x.strip() for x in (normalization_id,input_digest,extraction_revision)): raise ValueError("extraction identity is required")
    if not facts: raise ValueError("facts are required")
    if status not in {"PROPOSED","ACCEPTED","REJECTED"}: raise ValueError("invalid extraction status")
    fs=tuple(sorted(set(x.strip() for x in facts if x.strip())))
    if not fs: raise ValueError("facts cannot be empty")
    patterns=tuple(sorted(set(f for f in fs if ":" in f)))
    relations=tuple(sorted(set((f.split(":",1)[0],"contains",f) for f in fs if ":" in f)))
    c={"normalization_id":normalization_id,"input_digest":input_digest,"patterns":patterns,"relations":relations,"extraction_revision":extraction_revision,"status":status}
    eid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return ExtractedPattern(eid,normalization_id,input_digest,patterns,relations,extraction_revision,status)
def extraction_is_deterministic(*,result): return result.patterns==tuple(sorted(result.patterns)) and result.relations==tuple(sorted(result.relations))
def may_generate_candidate_contract(*,result): return result.status=="ACCEPTED" and extraction_is_deterministic(result=result)
