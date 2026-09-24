"""Execution result and verification feedback boundary (E8.06)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class VerificationFeedback:
    feedback_id:str; contract_id:str; contract_digest:str; execution_id:str; scope:str; expected_result:str; actual_result:str; evidence_refs:tuple[str,...]; verdict:str; deviation:str; status:str

def record_verification_feedback(*,contract_id,contract_digest,execution_id,scope,expected_result,actual_result,evidence_refs,verdict,deviation,status="RECORDED"):
    if not all(x.strip() for x in (contract_id,contract_digest,execution_id,scope,expected_result,actual_result,deviation)): raise ValueError("complete verification fields are required")
    if not evidence_refs: raise ValueError("verification requires evidence")
    if verdict not in {"PASS","PARTIAL","FAIL","INCONCLUSIVE"}: raise ValueError("invalid verdict")
    if status not in {"RECORDED","REVIEWED","REJECTED"}: raise ValueError("invalid status")
    refs=tuple(sorted(set(evidence_refs)))
    c=dict(contract_id=contract_id,contract_digest=contract_digest,execution_id=execution_id,scope=scope.strip(),expected_result=expected_result.strip(),actual_result=actual_result.strip(),evidence_refs=refs,verdict=verdict,deviation=deviation.strip(),status=status)
    fid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return VerificationFeedback(fid,**c)

def may_enter_learning(*,feedback): return feedback.status in {"RECORDED","REVIEWED"} and bool(feedback.evidence_refs)
def is_contract_bound(*,feedback,contract_id,contract_digest,scope): return feedback.contract_id==contract_id and feedback.contract_digest==contract_digest and feedback.scope==scope
def creates_execution_authority(*,feedback): return False
