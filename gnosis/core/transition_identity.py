"""Canonical identity for a Core transition record."""
from __future__ import annotations
from .types import TransitionRecord, _stable_hash

def canonical_transition_payload(record: TransitionRecord) -> dict:
    return {
        "from_state_id": record.from_state_id,
        "to_state_id": record.to_state_id,
        "candidate_id": record.candidate_id,
        "test_passed": record.test_result.passed,
        "test_reasons": list(record.test_result.reasons),
        "accepted": record.accepted,
        "reason": record.reason,
        "test_rule_id": record.test_rule_id,
    }

def transition_digest(record: TransitionRecord) -> str:
    return _stable_hash(canonical_transition_payload(record))

def transition_id(record: TransitionRecord) -> str:
    return f"transition:{transition_digest(record)}"

def verify_transition_identity(record: TransitionRecord, supplied_id: str) -> bool:
    return supplied_id == transition_id(record)
