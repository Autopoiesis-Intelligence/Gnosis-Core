"""Scope authorization for external machine transfers.

Repository membership is not sufficient: the participant must be ACTIVE and
the target repository must be explicitly listed in repository_scope.
"""
from __future__ import annotations
from dataclasses import dataclass
from .machine_participant import MachineParticipant, ParticipantState

@dataclass(frozen=True)
class TransferAuthorization:
    authorized: bool
    reasons: tuple[str, ...]

def authorize_transfer(participant: MachineParticipant, target_repository: str) -> TransferAuthorization:
    reasons: list[str] = []
    if participant.state is not ParticipantState.ACTIVE:
        reasons.append(f"participant state is {participant.state.value}")
    if target_repository not in participant.repository_scope:
        reasons.append("target repository is outside participant scope")
    return TransferAuthorization(not reasons, tuple(reasons))
