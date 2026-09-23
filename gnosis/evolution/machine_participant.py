"""Machine participant identity and fail-closed revocation state.

Identity is metadata only; it grants no Core or filesystem authority.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class ParticipantState(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"

@dataclass(frozen=True)
class MachineParticipant:
    machine_id: str
    participant_id: str
    repository_scope: tuple[str, ...]
    state: ParticipantState = ParticipantState.PENDING
    provenance_id: str | None = None
    revoked_at: str | None = None

    def can_submit_transfer(self) -> bool:
        return self.state is ParticipantState.ACTIVE

    def revoke(self, revoked_at: str) -> "MachineParticipant":
        if self.state is ParticipantState.REVOKED:
            return self
        return MachineParticipant(
            machine_id=self.machine_id,
            participant_id=self.participant_id,
            repository_scope=self.repository_scope,
            state=ParticipantState.REVOKED,
            provenance_id=self.provenance_id,
            revoked_at=revoked_at,
        )
