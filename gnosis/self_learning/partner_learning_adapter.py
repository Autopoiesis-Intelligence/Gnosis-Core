"""E8.23 canonical adapter boundary."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib,json
@dataclass(frozen=True)
class CanonicalPartnerCommitRequest:
    request_id:str; candidate_id:str; result_id:str; contract_id:str; provenance_digest:str; evidence_refs:tuple[str,...]; state_digest:str; status:str

def _request_digest(request: CanonicalPartnerCommitRequest) -> str:
    c=dict(candidate_id=request.candidate_id,result_id=request.result_id,contract_id=request.contract_id,provenance_digest=request.provenance_digest,evidence_refs=tuple(sorted(set(request.evidence_refs))),state_digest=request.state_digest,status=request.status)
    return "sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def build_request(*,candidate_id,result_id,contract_id,provenance_digest,evidence_refs,state_digest,admission_verified):
    if not admission_verified: raise ValueError("partner admission is not verified")
    if not all(x.strip() for x in (candidate_id,result_id,contract_id,provenance_digest,state_digest)): raise ValueError("canonical identity fields required")
    if not evidence_refs: raise ValueError("evidence required")
    c=dict(candidate_id=candidate_id,result_id=result_id,contract_id=contract_id,provenance_digest=provenance_digest,evidence_refs=tuple(sorted(set(evidence_refs))),state_digest=state_digest,status="READY_FOR_CANONICAL_COMMIT")
    rid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return CanonicalPartnerCommitRequest(rid,**c)

def may_submit(*,request):
    return request.status=="READY_FOR_CANONICAL_COMMIT" and request.request_id==_request_digest(request)
