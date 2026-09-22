"""Canonical candidate binding digest and anti-rebinding validation."""
from __future__ import annotations
from gnosis.core.types import Candidate, State, _stable_hash
from gnosis.core.state_identity import state_digest

def candidate_binding_digest(candidate: Candidate, parent: State) -> str:
    return _stable_hash({
        "candidate_id": candidate.candidate_id,
        "parent_state_id": parent.state_id,
        "parent_state_digest": state_digest(parent),
        "proposed_state_content_id": candidate.proposed_state.content_id,
    })

def verify_candidate_binding(candidate: Candidate, parent: State, expected_digest: str) -> bool:
    if candidate.parent_state_id != parent.state_id:
        return False
    return candidate_binding_digest(candidate,parent)==expected_digest
