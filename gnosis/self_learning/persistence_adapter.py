"""E8.24 persistence transaction adapter contract."""
from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class PersistenceCommitPlan:
    request_id:str; state_digest:str; candidate_id:str; audit_event_type:str; idempotency_key:str

def build_commit_plan(*,request_id,state_digest,candidate_id,audit_event_type="PARTNER_LEARNING_COMMIT",idempotency_key):
    if not all(x.strip() for x in (request_id,state_digest,candidate_id,audit_event_type,idempotency_key)): raise ValueError("complete persistence identity required")
    return PersistenceCommitPlan(request_id,state_digest,candidate_id,audit_event_type,idempotency_key)

def failure_requires_rollback(*,failure_point): return failure_point in {"state_insert","candidate_insert","transition_insert","audit_insert","head_update","commit"}

def commit_proof_complete(*,head_state_id,transition_to_state_id,transition_from_state_id,previous_head,candidate_parent_state_id,audit_verified):
    return (head_state_id==transition_to_state_id and transition_from_state_id==previous_head and candidate_parent_state_id==transition_from_state_id and audit_verified)
