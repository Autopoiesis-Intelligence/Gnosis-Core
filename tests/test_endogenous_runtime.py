from dataclasses import replace

from gnosis.core import Budget, Engine, State
from gnosis.reflection.analyzer import ReflectionReport
from gnosis.reflection.endogenous_runtime import generate_from_cumulative_reflection
from gnosis.reflection.runtime import CumulativeReflectionReport
from gnosis.reflection.memory_evidence import EvolutionEvidence


def test_cumulative_evolution_memory_is_bound_into_next_candidate():
    state = State(elements={"a": 1})
    engine = Engine(state=state, budget=Budget(total=3))
    proposal = type("P", (), {
        "proposal_id": "proposal-1",
        "finding_id": "finding-1",
        "rule_id": "rule-1",
        "current_version": 1,
        "proposed_version": 2,
        "hypothesis": "bounded endogenous hypothesis",
        "evidence_refs": ("finding-1",),
    })()
    report = ReflectionReport(proposals=(proposal,))
    evidence = EvolutionEvidence(
        memory_id="memory-1",
        candidate_id="candidate-1",
        transition_id="transition-1",
        state_id="state-1",
        outcome="accepted",
    )
    cumulative = CumulativeReflectionReport(
        current=report,
        history=None,
        recurring_unresolved=(),
        evolution_evidence=(evidence,),
    )

    generation = generate_from_cumulative_reflection(engine, cumulative)

    assert len(generation.candidates) == 1
    node = generation.candidates[0].proposed_state.elements["proposal-1"]
    assert node["memory_evidence_refs"] == ("memory-1",)
    assert node["historical_memory_outcomes"] == ("accepted",)
    assert node["memory_signature"] == ("memory-1",)


def test_cumulative_adapter_is_read_only():
    state = State(elements={"a": 1})
    engine = Engine(state=state, budget=Budget(total=3))
    before = engine.state
    report = ReflectionReport(proposals=())
    cumulative = CumulativeReflectionReport(
        current=report,
        history=None,
        recurring_unresolved=(),
        evolution_evidence=(),
    )

    generation = generate_from_cumulative_reflection(engine, cumulative)

    assert generation.candidates == ()
    assert engine.state == before
