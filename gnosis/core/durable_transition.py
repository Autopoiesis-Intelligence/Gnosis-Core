"""Durable identity for a committed Core transition."""
from __future__ import annotations
from dataclasses import dataclass
from .types import TransitionRecord
from .transition_identity import transition_id, verify_transition_identity

@dataclass(frozen=True)
class DurableTransition:
    transition_id: str
    record: TransitionRecord
    provenance_id: str
    audit_record_id: str
    evidence_digest: str

    def validate(self) -> None:
        if not self.provenance_id or not self.audit_record_id or not self.evidence_digest:
            raise ValueError("durable transition identities are required")
        if not verify_transition_identity(self.record, self.transition_id):
            raise ValueError("transition identity does not match transition record")
        if not self.record.from_state_id or not self.record.to_state_id:
            raise ValueError("transition state identities are required")
