"""Explicit semantics for State identity layers."""
from __future__ import annotations
from dataclasses import dataclass
from gnosis.core.types import State, Candidate
from gnosis.core.state_identity import state_digest

@dataclass(frozen=True)
class StateIdentity:
    state_id: str
    content_id: str
    state_digest: str

def identify_state(state: State) -> StateIdentity:
    return StateIdentity(state.state_id,state.content_id,state_digest(state))

def validate_candidate_parent(candidate: Candidate, parent: State, parent_digest: str) -> None:
    if candidate.parent_state_id != parent.state_id:
        raise ValueError("candidate parent_state_id does not match parent state_id")
    if state_digest(parent) != parent_digest:
        raise ValueError("candidate parent state digest mismatch")

def validate_candidate_content(candidate: Candidate) -> None:
    if candidate.proposed_state.content_id != candidate.proposed_state.content_id:
        raise AssertionError("unreachable content identity inconsistency")
