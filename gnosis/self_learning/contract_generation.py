"""Deterministic contract generation gate (E8.14)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class GeneratedContract:
    contract_id:str; proposal_id:str; proposal_digest:str; collaboration_type:str; scope:str; rights_profile:str; acceptance_criteria:tuple[str,...]; evidence_requirements:tuple[str,...]; transfer_boundary:str; status:str

def generate_contract(*,proposal_id,proposal_digest,collaboration_type,scope,rights_profile,acceptance_criteria,evidence_requirements,transfer_boundary,accepted=True,status="DRAFT"):
    if not accepted: raise ValueError("proposal must be accepted")
    if collaboration_type not in {"OPEN_NONCOMMERCIAL","COMMERCIAL_PARTNERSHIP"}: raise ValueError("invalid collaboration type")
    if not all(x.strip() for x in (proposal_id,proposal_digest,scope,rights_profile,transfer_boundary)): raise ValueError("complete contract fields are required")
    if not acceptance_criteria or not evidence_requirements: raise ValueError("contract requires acceptance and evidence criteria")
    if status not in {"DRAFT","READY_FOR_EXECUTION","REJECTED"}: raise ValueError("invalid status")
    ac=tuple(sorted(set(acceptance_criteria))); er=tuple(sorted(set(evidence_requirements)))
    c=dict(proposal_id=proposal_id,proposal_digest=proposal_digest,collaboration_type=collaboration_type,scope=scope.strip(),rights_profile=rights_profile.strip(),acceptance_criteria=ac,evidence_requirements=er,transfer_boundary=transfer_boundary.strip(),status=status)
    cid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return GeneratedContract(cid,**c)

def binds_proposal(*,contract,proposal_id,proposal_digest): return contract.proposal_id==proposal_id and contract.proposal_digest==proposal_digest
def may_execute(*,contract): return contract.status=="READY_FOR_EXECUTION"
