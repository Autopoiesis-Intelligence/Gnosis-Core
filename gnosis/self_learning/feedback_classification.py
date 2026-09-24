"""Partner learning feedback classification (E8.19)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
CLASSES={"SUCCESS_SIGNAL","COUNTEREXAMPLE","FAILURE","INCONCLUSIVE"}
@dataclass(frozen=True)
class FeedbackClassification:
    classification_id:str; result_id:str; outcome_class:str; learning_route:str; reusable:bool; evidence_refs:tuple[str,...]; rationale:str; status:str

def classify_partner_feedback(*,result_id,outcome_class,evidence_refs,rationale,status="PROPOSED"):
    if not result_id.strip() or not rationale.strip(): raise ValueError("result identity and rationale are required")
    if outcome_class not in CLASSES: raise ValueError("invalid outcome class")
    if not evidence_refs: raise ValueError("feedback classification requires evidence")
    if status not in {"PROPOSED","VERIFIED","REJECTED"}: raise ValueError("invalid status")
    routes={"SUCCESS_SIGNAL":"LEARNING_CANDIDATE","COUNTEREXAMPLE":"LEARNING_CANDIDATE","FAILURE":"DIAGNOSTIC_ONLY","INCONCLUSIVE":"HOLD"}
    reusable=outcome_class in {"SUCCESS_SIGNAL","COUNTEREXAMPLE"}
    c=dict(result_id=result_id,outcome_class=outcome_class,learning_route=routes[outcome_class],reusable=reusable,evidence_refs=tuple(sorted(set(evidence_refs))),rationale=rationale.strip(),status=status)
    cid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return FeedbackClassification(cid,**c)

def may_form_learning_candidate(*,classification): return classification.status=="VERIFIED" and classification.learning_route=="LEARNING_CANDIDATE"
def may_enter_durable_learning(*,classification): return False
