"""Partner core transfer boundary (E8.15)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class TransferManifest:
    manifest_id:str; contract_id:str; partner_scope:str; core_artifacts:tuple[str,...]; evidence_artifacts:tuple[str,...]; excluded_artifacts:tuple[str,...]; transfer_policy:str; status:str

def create_transfer_manifest(*,contract_id,partner_scope,core_artifacts,evidence_artifacts,excluded_artifacts,transfer_policy,status="PROPOSED"):
    if not all(x.strip() for x in (contract_id,partner_scope,transfer_policy)): raise ValueError("complete transfer fields are required")
    if not partner_scope.startswith("partner:"): raise ValueError("partner scope required")
    if not core_artifacts: raise ValueError("minimal core artifacts required")
    if not excluded_artifacts: raise ValueError("explicit exclusions required")
    if status not in {"PROPOSED","REVIEW_REQUIRED","APPROVED","REJECTED"}: raise ValueError("invalid status")
    core=tuple(sorted(set(core_artifacts))); ev=tuple(sorted(set(evidence_artifacts))); ex=tuple(sorted(set(excluded_artifacts)))
    if any("AI_CONTEXT" in x or "Research-Memory" in x or "research-memory" in x for x in core): raise ValueError("internal memory cannot be transferred as core artifact")
    if any(x in ex for x in core): raise ValueError("artifact cannot be both transferred and excluded")
    c=dict(contract_id=contract_id,partner_scope=partner_scope.strip(),core_artifacts=core,evidence_artifacts=ev,excluded_artifacts=ex,transfer_policy=transfer_policy.strip(),status=status)
    mid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return TransferManifest(mid,**c)

def may_transfer(*,manifest,contract_ready): return manifest.status=="APPROVED" and contract_ready
def includes_internal_memory(*,manifest): return any("AI_CONTEXT" in x or "Research-Memory" in x or "research-memory" in x for x in manifest.core_artifacts)

def grants_execution_authority(*,manifest): return False
