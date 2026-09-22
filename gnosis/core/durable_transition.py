"""Durable identity for a committed Core transition."""
from __future__ import annotations
from dataclasses import dataclass
from .types import TransitionRecord

@dataclass(frozen=True)
class DurableTransition:
    transition_id: str
    record: TransitionRecord
    provenance_id: str
    audit_record_id: str
    evidence_digest: str

    def validate(self) -> None:
        if not self.transition_id or not self.provenance_id or not self.audit_record_id or not self.evidence_digest:
            raise ValueError("durable transition identities are required")
        if self.record.candidate_id != self.transition_id.split(":",1)[-1] and not self.transition_id.startswith("transition:"):
            raise ValueError("transition identity must be explicitly namespaced")
        if not self.record.from_state_id or not self.record.to_state_id:
            raise ValueError("transition state identities are required")
