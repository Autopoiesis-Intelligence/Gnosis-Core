"""Partner result return path to learning candidate (E8.17)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class PartnerResultEvidence:
    result_id:str; delivery_id:str; contract_id:str; partner_scope:str; result_digest:str; evidence_refs:tuple[str,...]; outcome_class:str; status:str

def record_partner_result(*,delivery_id,contract_id,partner_scope,result_digest,evidence_refs,outcome_class,status="PROPOSED"):
    if not all(x.strip() for x in (delivery_id,contract_id,partner_scope,result_digest)): raise ValueError("complete result fields are required")
    if not partner_scope.startswith("partner:"): raise ValueError("partner scope required")
    if not evidence_refs: raise ValueError("partner result requires evidence")
    if outcome_class not in {"SUCCESS_SIGNAL","COUNTEREXAMPLE","INCONCLUSIVE"}: raise ValueError("invalid outcome class")
    if status not in {"PROPOSED","VERIFIED","REJECTED"}: raise ValueError("invalid status")
    refs=tuple(sorted(set(evidence_refs)))
    c=dict(delivery_id=delivery_id,contract_id=contract_id,partner_scope=partner_scope.strip(),result_digest=result_digest,evidence_refs=refs,outcome_class=outcome_class,status=status)
    rid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return PartnerResultEvidence(rid,**c)

def may_enter_learning(*,result,receipt_received,core_verified): return result.status=="VERIFIED" and receipt_received and core_verified and result.outcome_class in {"SUCCESS_SIGNAL","COUNTEREXAMPLE"}
def binds_delivery(*,result,delivery_id,contract_id): return result.delivery_id==delivery_id and result.contract_id==contract_id
