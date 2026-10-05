"""Governed self-learning proposal boundary (E7.93)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class LearningProposal:
    proposal_id:str; candidate_id:str; evaluation_id:str; base_state_digest:str; objective:str; scope:str; evidence_refs:tuple[str,...]; proposal_revision:str; status:str
def create_proposal(*,candidate_id,evaluation_id,base_state_digest,objective,scope,evidence_refs,proposal_revision="r1",status="PROPOSED"):
    if not all(x.strip() for x in (candidate_id,evaluation_id,base_state_digest,objective,scope,proposal_revision)): raise ValueError("proposal identity is required")
    if not evidence_refs: raise ValueError("proposal evidence is required")
    if status not in {"PROPOSED","APPROVED","REJECTED","BLOCKED","EXPIRED"}: raise ValueError("invalid proposal status")
    c={"candidate_id":candidate_id,"evaluation_id":evaluation_id,"base_state_digest":base_state_digest,"objective":objective.strip(),"scope":scope.strip(),"evidence_refs":tuple(sorted(set(evidence_refs))),"proposal_revision":proposal_revision,"status":status}
    pid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return LearningProposal(pid,candidate_id,evaluation_id,base_state_digest,c["objective"],c["scope"],c["evidence_refs"],proposal_revision,status)
def may_propose(*, proposal, shadow_outcome, shadow_evaluation_id=None):
    if proposal.status != "PROPOSED" or shadow_outcome != "PASS" or not proposal.evidence_refs:
        return False
    if shadow_evaluation_id is None:
        return False
    return shadow_evaluation_id == proposal.evaluation_id
def proposal_grants_execution_authority(*,proposal): return False
def proposal_is_bound_to_state(*,proposal,current_state_digest): return proposal.base_state_digest==current_state_digest
