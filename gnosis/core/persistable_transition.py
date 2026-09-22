"""Core transition identity and immutable record contract."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Any
from .types import TransitionRecord
from .transition_identity import transition_id

@dataclass(frozen=True)
class PersistableTransition:
    record: TransitionRecord

    @property
    def transition_id(self) -> str:
        return transition_id(self.record)

    def payload(self) -> Mapping[str, Any]:
        return {
            "from_state_id": self.record.from_state_id,
            "to_state_id": self.record.to_state_id,
            "candidate_id": self.record.candidate_id,
            "test_passed": self.record.test_result.passed,
            "test_reasons": tuple(self.record.test_result.reasons),
            "accepted": self.record.accepted,
            "reason": self.record.reason,
            "test_rule_id": self.record.test_rule_id,
        }
