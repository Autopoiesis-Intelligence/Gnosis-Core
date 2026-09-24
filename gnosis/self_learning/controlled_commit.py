"""Fail-closed controlled commit boundary for governed self-learning (E7.95)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class ControlledCommit:
    commit_id:str; proposal_id:str; governance_decision_id:str; base_state_digest:str; resulting_state_digest:str; transition_digest:str; evidence_refs:tuple[str,...]; status:str
def create_controlled_commit(*,proposal_id,governance_decision_id,base_state_digest,resulting_state_digest,transition_digest,evidence_refs,status="PROPOSED"):
    if not all(x.strip() for x in (proposal_id,governance_decision_id,base_state_digest,resulting_state_digest,transition_digest)): raise ValueError("commit identity is required")
    if not evidence_refs: raise ValueError("commit evidence is required")
    if status not in {"PROPOSED","COMMITTED","REJECTED","ROLLED_BACK","BLOCKED"}: raise ValueError("invalid commit status")
    c={"proposal_id":proposal_id,"governance_decision_id":governance_decision_id,"base_state_digest":base_state_digest,"resulting_state_digest":resulting_state_digest,"transition_digest":transition_digest,"evidence_refs":tuple(sorted(set(evidence_refs))),"status":status}
    cid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return ControlledCommit(cid,proposal_id,governance_decision_id,base_state_digest,resulting_state_digest,transition_digest,c["evidence_refs"],status)
def may_commit(*,commit,governance_outcome,current_state_digest,required_result_digest):
    return commit.status=="PROPOSED" and governance_outcome=="APPROVED" and commit.base_state_digest==current_state_digest and commit.resulting_state_digest==required_result_digest and bool(commit.evidence_refs) and commit.base_state_digest!=commit.resulting_state_digest
def is_fail_closed(*,commit,governance_outcome,current_state_digest,required_result_digest):
    return not may_commit(commit=commit,governance_outcome=governance_outcome,current_state_digest=current_state_digest,required_result_digest=required_result_digest)
def grants_authority(*,commit): return False
