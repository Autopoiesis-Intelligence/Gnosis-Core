"""Deterministic candidate contract generation boundary (E7.91)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class CandidateContract:
    candidate_id:str; extraction_id:str; pattern_refs:tuple[str,...]; relation_refs:tuple[str,...]; objective:str; scope:str; evidence_refs:tuple[str,...]; contract_revision:str; status:str
def create_candidate_contract(*,extraction_id,pattern_refs,relation_refs,objective,scope,evidence_refs,contract_revision="r1",status="PROPOSED"):
    if not all(x.strip() for x in (extraction_id,objective,scope,contract_revision)): raise ValueError("candidate identity is required")
    if not pattern_refs and not relation_refs: raise ValueError("candidate requires pattern or relation references")
    if not evidence_refs: raise ValueError("candidate requires evidence references")
    if status not in {"PROPOSED","SHADOW","REJECTED","ACCEPTED"}: raise ValueError("invalid candidate status")
    c={"extraction_id":extraction_id,"pattern_refs":tuple(sorted(set(pattern_refs))),"relation_refs":tuple(sorted(set(relation_refs))),"objective":objective.strip(),"scope":scope.strip(),"evidence_refs":tuple(sorted(set(evidence_refs))),"contract_revision":contract_revision,"status":status}
    cid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return CandidateContract(cid,extraction_id,c["pattern_refs"],c["relation_refs"],c["objective"],c["scope"],c["evidence_refs"],contract_revision,status)
def candidate_is_well_formed(*,candidate):
    return bool(candidate.candidate_id and candidate.extraction_id and candidate.pattern_refs+candidate.relation_refs and candidate.evidence_refs and candidate.objective and candidate.scope)
def may_enter_shadow_evaluation(*,candidate): return candidate.status in {"PROPOSED","SHADOW"} and candidate_is_well_formed(candidate=candidate)
def candidate_grants_execution_authority(*,candidate): return False
