from gnosis.core import Budget, Candidate, Engine, State
from gnosis.reflection.runtime import run_endogenous


def _seed_candidate(state):
    return Candidate(
        parent_state_id=state.state_id,
        proposed_state=state.with_elements({"seed": 1}),
        origin="external:seed",
    )


def test_endogenous_runtime_bridge_uses_canonical_engine_transition_path():
    state = State(elements={"a": 1})
    engine = Engine(
        state=state,
        budget=Budget(total=4),
        test_fn=lambda _state, candidate: candidate.origin == "reflection:endogenous",
    )

    first = engine.step(_seed_candidate(engine.state))
    second = engine.step(_seed_candidate(engine.state))

    assert not first.accepted
    assert not second.accepted
    assert engine.state.state_id == state.state_id

    records = run_endogenous(engine, max_steps=1)

    assert len(records) == 1
    assert records[0].accepted
    assert records[0].from_state_id == state.state_id
    assert records[0].candidate_id.startswith("candidate:")
    assert engine.state.state_id != state.state_id


def test_endogenous_runtime_bridge_does_not_commit_when_canonical_test_rejects():
    state = State(elements={"a": 1})
    engine = Engine(
        state=state,
        budget=Budget(total=3),
        test_fn=lambda _state, _candidate: False,
    )
    engine.step(_seed_candidate(engine.state))
    engine.step(_seed_candidate(engine.state))

    records = run_endogenous(engine, max_steps=1)

    assert len(records) == 1
    assert not records[0].accepted
    assert engine.state.state_id == state.state_id
