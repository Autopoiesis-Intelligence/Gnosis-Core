"""Partner learning candidate -> durable commit gate adapter (E8.20)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class LearningAdmission:
    admission_id:str; classification_id:str; result_id:str; candidate_digest:str; evidence_refs:tuple[str,...]; admission_status:str; commit_authorized:bool

def admit_partner_candidate(*,classification_id,result_id,candidate_digest,evidence_refs,classification_verified,replay_verified,receipt_received,core_verified):
    if not all(x.strip() for x in (classification_id,result_id,candidate_digest)): raise ValueError("candidate identity is required")
    if not evidence_refs: raise ValueError("candidate evidence is required")
    if not (classification_verified and replay_verified and receipt_received and core_verified):
        raise ValueError("all trust gates must be verified before admission")
    refs=tuple(sorted(set(evidence_refs)))
    c=dict(classification_id=classification_id,result_id=result_id,candidate_digest=candidate_digest,evidence_refs=refs,admission_status="ADMITTED",commit_authorized=True)
    aid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return LearningAdmission(aid,**c)

def may_commit(*,admission): return admission.admission_status=="ADMITTED" and admission.commit_authorized
