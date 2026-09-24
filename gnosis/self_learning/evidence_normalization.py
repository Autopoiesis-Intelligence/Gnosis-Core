"""Deterministic normalization boundary for admitted learning evidence (E7.89)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class NormalizedEvidence:
    normalization_id:str; admission_id:str; source_digest:str; normalized_digest:str; schema_version:str; normalized_facts:tuple[str,...]; redactions:tuple[str,...]; status:str
def normalize_evidence(*,admission_id,source_digest,facts,schema_version,redactions=(),status="PROPOSED"):
    if not all(x.strip() for x in (admission_id,source_digest,schema_version)): raise ValueError("normalization identity is required")
    if not facts: raise ValueError("facts are required")
    if status not in {"PROPOSED","ACCEPTED","REJECTED"}: raise ValueError("invalid normalization status")
    nf=tuple(sorted(set(x.strip() for x in facts if x.strip())))
    if not nf: raise ValueError("facts cannot be empty")
    nr=tuple(sorted(set(x.strip() for x in redactions if x.strip())))
    c={"admission_id":admission_id,"source_digest":source_digest,"normalized_facts":nf,"schema_version":schema_version,"redactions":nr,"status":status}
    nd="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    nid="sha256:"+hashlib.sha256(json.dumps({"admission_id":admission_id,"source_digest":source_digest,"normalized_digest":nd,"schema_version":schema_version},sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return NormalizedEvidence(nid,admission_id,source_digest,nd,schema_version,nf,nr,status)
def normalization_is_deterministic(*,evidence): return bool(evidence.normalized_digest) and tuple(evidence.normalized_facts)==tuple(sorted(evidence.normalized_facts))
def may_enter_pattern_extraction(*,evidence): return evidence.status=="ACCEPTED" and normalization_is_deterministic(evidence=evidence)
