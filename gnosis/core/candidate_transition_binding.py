"""Cross-binding contract between a verified Candidate and its Transition."""
from __future__ import annotations
from gnosis.core.types import Candidate, TransitionRecord, State
from gnosis.core.candidate_binding import candidate_binding_digest
from gnosis.core.state_identity import state_digest

def verify_candidate_transition_binding(
    candidate: Candidate,
    parent: State,
    transition: TransitionRecord,
    expected_binding_digest: str,
) -> None:
    if transition.candidate_id != candidate.candidate_id:
        raise ValueError("transition candidate_id mismatch")
    if transition.from_state_id != parent.state_id:
        raise ValueError("transition parent state mismatch")
    if transition.to_state_id != candidate.proposed_state.state_id:
        raise ValueError("transition proposed state mismatch")
    if candidate_binding_digest(candidate,parent) != expected_binding_digest:
        raise ValueError("candidate binding digest mismatch")
    if state_digest(candidate.proposed_state) != state_digest(candidate.proposed_state):
        raise ValueError("unreachable proposed state identity inconsistency")
