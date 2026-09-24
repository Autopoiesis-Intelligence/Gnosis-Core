"""Evidence-gated integration of verification feedback into learning (E8.07)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class LearningFeedbackAdmission:
    admission_id:str; feedback_id:str; contract_id:str; scope:str; verdict:str; evidence_refs:tuple[str,...]; learning_class:str; status:str

def admit_feedback(*,feedback_id,contract_id,scope,verdict,evidence_refs,learning_class,status="PROPOSED"):
    if not all(x.strip() for x in (feedback_id,contract_id,scope)): raise ValueError("feedback identity is required")
    if not evidence_refs: raise ValueError("learning admission requires evidence")
    if verdict not in {"PASS","PARTIAL","FAIL","INCONCLUSIVE"}: raise ValueError("invalid verdict")
    if learning_class not in {"LEARNING_SIGNAL","COUNTEREXAMPLE","NO_ADMISSION","REVIEW_REQUIRED"}: raise ValueError("invalid learning class")
    if status not in {"PROPOSED","ADMITTED","REJECTED","BLOCKED"}: raise ValueError("invalid status")
    refs=tuple(sorted(set(evidence_refs)))
    if verdict=="FAIL" and learning_class=="LEARNING_SIGNAL": raise ValueError("fail cannot silently become positive learning signal")
    if verdict=="INCONCLUSIVE" and learning_class=="LEARNING_SIGNAL": raise ValueError("inconclusive cannot become learning signal")
    c=dict(feedback_id=feedback_id,contract_id=contract_id,scope=scope.strip(),verdict=verdict,evidence_refs=refs,learning_class=learning_class,status=status)
    aid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return LearningFeedbackAdmission(aid,**c)

def may_enter_learning(*,admission): return admission.status=="ADMITTED" and admission.learning_class in {"LEARNING_SIGNAL","COUNTEREXAMPLE"}
def requires_review(*,admission): return admission.learning_class=="REVIEW_REQUIRED" or admission.verdict=="INCONCLUSIVE"
def creates_execution_authority(*,admission): return False
