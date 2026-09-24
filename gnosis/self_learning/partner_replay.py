"""Partner result provenance replay gate (E8.18)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class PartnerReplayDecision:
    replay_id:str; result_id:str; delivery_id:str; manifest_id:str; contract_id:str; core_digest:str; result_digest:str; decision:str; evidence_refs:tuple[str,...]

def replay_partner_result(*,result_id,delivery_id,manifest_id,contract_id,core_digest,result_digest,expected_core_digest,expected_delivery_id,expected_manifest_id,expected_contract_id,evidence_refs):
    if not all(x.strip() for x in (result_id,delivery_id,manifest_id,contract_id,core_digest,result_digest)): raise ValueError("complete replay identity is required")
    if not evidence_refs: raise ValueError("replay requires evidence")
    ok=(core_digest==expected_core_digest and delivery_id==expected_delivery_id and manifest_id==expected_manifest_id and contract_id==expected_contract_id)
    decision="REPLAY_VERIFIED" if ok else "REPLAY_REJECTED"
    refs=tuple(sorted(set(evidence_refs)))
    c=dict(result_id=result_id,delivery_id=delivery_id,manifest_id=manifest_id,contract_id=contract_id,core_digest=core_digest,result_digest=result_digest,decision=decision,evidence_refs=refs)
    rid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return PartnerReplayDecision(rid,**c)

def may_enter_learning(*,decision): return decision.decision=="REPLAY_VERIFIED"
