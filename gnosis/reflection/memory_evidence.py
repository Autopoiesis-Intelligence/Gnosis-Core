"""Read-only projection of durable evolution memory into Reflection evidence."""
from __future__ import annotations
from dataclasses import dataclass
from gnosis.storage.evolution_memory import EvolutionMemoryRecord

@dataclass(frozen=True)
class EvolutionEvidence:
    memory_id: str
    candidate_id: str
    transition_id: str
    outcome: str
    evidence: tuple[str, ...]
    state_id: str = ""
    proposal_id: str | None = None
    proposal_report_id: str | None = None


def project_evolution_memory(records: tuple[EvolutionMemoryRecord, ...], *, limit: int = 100) -> tuple[EvolutionEvidence, ...]:
    """Expose verified memory as evidence only; never creates authority or candidates."""
    if limit < 1:
        raise ValueError("limit must be >= 1")
    return tuple(
        EvolutionEvidence(
            memory_id=r.memory_id,
            candidate_id=r.candidate_id,
            transition_id=r.transition_id,
            outcome=r.outcome,
            evidence=r.evidence,
            state_id=r.state_id,
            proposal_id=r.proposal_id,
            proposal_report_id=r.proposal_report_id,
        )
        for r in records[:limit]
    )
