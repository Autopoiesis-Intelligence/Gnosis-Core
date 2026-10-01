"""Human/partner acceptance gate for auditable proposals (E8.04)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class ProposalDecision:
    decision_id:str; proposal_id:str; decision:str; actor_ref:str; reason:str; proposal_digest:str

def decide_proposal(*,proposal_id,proposal_digest,actor_ref,decision,reason):
    if not all(x.strip() for x in (proposal_id,proposal_digest,actor_ref,reason)): raise ValueError("complete decision fields are required")
    if decision not in {"ACCEPT","REJECT","REQUEST_CHANGES"}: raise ValueError("invalid decision")
    c=dict(proposal_id=proposal_id,proposal_digest=proposal_digest,actor_ref=actor_ref,decision=decision,reason=reason.strip())
    did="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return ProposalDecision(did,proposal_id,decision,actor_ref,reason.strip(),proposal_digest)

def may_activate(*, proposal_status, decision, proposal_id=None, proposal_digest=None, current_state_digest=None, proposal_state_digest=None):\n    if proposal_status != "PROPOSED" or decision.decision != "ACCEPT":\n        return False\n    if proposal_id is None or proposal_digest is None:\n        return False\n    if not decision_binds_proposal(decision=decision, proposal_id=proposal_id, proposal_digest=proposal_digest):\n        return False\n    if current_state_digest is None or proposal_state_digest is None:\n        return False\n    return current_state_digest == proposal_state_digest
def decision_binds_proposal(*,decision,proposal_id,proposal_digest): return decision.proposal_id==proposal_id and decision.proposal_digest==proposal_digest
def creates_execution_authority(*,decision): return False
