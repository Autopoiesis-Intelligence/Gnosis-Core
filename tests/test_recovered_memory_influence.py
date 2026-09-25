from gnosis.storage.evolution_memory import EvolutionMemoryRecord
from gnosis.self_learning.recovered_memory_influence import (
    build_influence_from_recovered_memory,
)


def make_memory():
    return EvolutionMemoryRecord(
        memory_id="memory:1",
        instance_id="instance:1",
        candidate_id="candidate:1",
        transition_id="transition:1",
        state_id="state:1",
        proposal_id=None,
        outcome="rejected",
        evidence=("evidence:failure",),
        created_at="2026-09-25T00:00:00Z",
    )


def test_recovered_memory_becomes_bound_next_cycle_input():
    memory = make_memory()
    result = build_influence_from_recovered_memory(
        memory=memory,
        parent_cycle_id="cycle:2",
    )
    assert result.source_memory_id == memory.memory_id
    assert result.source_transition_id == memory.transition_id
    assert "evidence:failure" in result.next_cycle_input
    assert result.influence_digest.startswith("sha256:")


def test_empty_recovered_evidence_cannot_influence():
    memory = make_memory()
    memory = EvolutionMemoryRecord(
        memory_id=memory.memory_id,
        instance_id=memory.instance_id,
        candidate_id=memory.candidate_id,
        transition_id=memory.transition_id,
        state_id=memory.state_id,
        proposal_id=None,
        outcome=memory.outcome,
        evidence=(),
        created_at=memory.created_at,
    )
    try:
        build_influence_from_recovered_memory(
            memory=memory,
            parent_cycle_id="cycle:2",
        )
    except ValueError:
        return
    raise AssertionError("empty recovered evidence influenced next cycle")
