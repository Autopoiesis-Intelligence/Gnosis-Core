"""Verified evidence admission into the self-learning corpus (E7.88)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
ALLOWED={"VERIFIED_CLOSED","VERIFIED_ATTESTED","RESOLVED"}
BLOCKED={"OPEN","DISPUTED","REJECTED","UNKNOWN","BLOCKED"}
@dataclass(frozen=True)
class LearningEvidenceAdmission:
    admission_id:str; source_contract_id:str; verification_refs:tuple[str,...]; evidence_refs:tuple[str,...]; evidence_digest:str; privacy_classification:str; learning_scope:str; status:str
def create_admission(*,source_contract_id,verification_refs,evidence_refs,evidence_digest,privacy_classification,learning_scope,status="PROPOSED"):
    if not all(x.strip() for x in (source_contract_id,evidence_digest,privacy_classification,learning_scope)): raise ValueError("admission identity is required")
    if not verification_refs or not evidence_refs: raise ValueError("verification and evidence references are required")
    if status not in {"PROPOSED","ADMITTED","REJECTED","BLOCKED"}: raise ValueError("invalid admission status")
    c={"source_contract_id":source_contract_id,"verification_refs":verification_refs,"evidence_refs":evidence_refs,"evidence_digest":evidence_digest,"privacy_classification":privacy_classification,"learning_scope":learning_scope,"status":status}
    aid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return LearningEvidenceAdmission(aid,source_contract_id,verification_refs,evidence_refs,evidence_digest,privacy_classification,learning_scope,status)
def may_admit(*,admission,source_state):
    return admission.status=="ADMITTED" and source_state in ALLOWED and bool(admission.verification_refs) and bool(admission.evidence_refs) and admission.privacy_classification in {"PUBLIC","SHAREABLE_ABSTRACTION","REDACTED"}
def creates_execution_authority(*,admission): return False
