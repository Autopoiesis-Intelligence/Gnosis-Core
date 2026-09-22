"""Recovery gate: no state resume without complete evolution integrity."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from gnosis.storage.evolution_integrity import verify_evolution_integrity, EvolutionIntegrity

@dataclass(frozen=True)
class RecoveryGateResult:
    allowed: bool
    integrity: EvolutionIntegrity | None
    reason: str | None

def recovery_pre_resume_gate(conn, transition_id: str) -> RecoveryGateResult:
    try:
        integrity=verify_evolution_integrity(conn,transition_id)
    except (KeyError, ValueError, TypeError, IndexError) as exc:
        return RecoveryGateResult(False,None,str(exc))
    return RecoveryGateResult(True,integrity,None)
