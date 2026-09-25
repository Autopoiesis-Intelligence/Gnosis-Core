"""R3.4.2 repeated bounded endogenous cycles."""
from gnosis.core import Engine, State
from gnosis.core.budget import Budget
from gnosis.self_learning.autonomous_cycle import run_one_endogenous_cycle

def test_repeated_endogenous_cycles_preserve_progress_and_bound():
    engine=Engine(state=State(elements={"a":1}), budget=Budget(total=3))
    engine.history.clear()
    transitions=[]
    for _ in range(3):
        result=run_one_endogenous_cycle(engine)
        assert result.generation.bounded
        assert result.transition is not None
        assert result.transition.accepted
        transitions.append(result.transition)
    assert len({t.transition_id for t in transitions}) == 3
    assert len({t.to_state_id for t in transitions}) == 3
    assert engine.state.state_id == transitions[-1].to_state_id
    assert engine.budget.remaining >= 0
