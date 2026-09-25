"""R3.2 semantic bridge: recovered EvolutionMemory -> next learning input."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from gnosis.storage.evolution_memory import EvolutionMemoryRecord


@dataclass(frozen=True)
class RecoveredLearningInfluence:
    source_memory_id: str
    source_transition_id: str
    evidence_refs: tuple[str, ...]
    next_cycle_input: tuple[str, ...]
    influence_digest: str


def build_influence_from_recovered_memory(
    *,
    memory: EvolutionMemoryRecord,
    parent_cycle_id: str,
) -> RecoveredLearningInfluence:
    if not parent_cycle_id.strip():
        raise ValueError("parent cycle identity is required")
    if not memory.memory_id or not memory.transition_id:
        raise ValueError("recovered memory identity is required")
    if memory.outcome not in {"accepted", "rejected", "inconclusive"}:
        raise ValueError("invalid recovered memory outcome")
    refs = tuple(sorted(set(str(x) for x in memory.evidence)))
    if not refs:
        raise ValueError("recovered memory has no evidence")

    next_input = (
        "parent_cycle:" + parent_cycle_id,
        "source_memory:" + memory.memory_id,
        "source_transition:" + memory.transition_id,
        *refs,
    )
    canonical = {
        "parent_cycle_id": parent_cycle_id,
        "memory_id": memory.memory_id,
        "transition_id": memory.transition_id,
        "evidence": refs,
        "next_input": next_input,
    }
    digest = "sha256:" + hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return RecoveredLearningInfluence(
        source_memory_id=memory.memory_id,
        source_transition_id=memory.transition_id,
        evidence_refs=refs,
        next_cycle_input=next_input,
        influence_digest=digest,
    )
