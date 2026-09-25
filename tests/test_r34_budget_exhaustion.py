"""R3.4.2 budget exhaustion must stop autonomous commits."""
import pytest
from gnosis.core import Engine, State
from gnosis.core.budget import Budget
from gnosis.self_learning.autonomous_cycle import run_one_endogenous_cycle

def test_budget_exhaustion_stops_next_cycle_without_commit():
    engine=Engine(state=State(elements={"a":1}), budget=Budget(limit=1))
    engine.history.clear()
    first=run_one_endogenous_cycle(engine)
    assert first.transition is not None
    before=engine.state.state_id
    # A second autonomous attempt must not create another committed transition.
    second=run_one_endogenous_cycle(engine)
    assert second.transition is None
    assert engine.state.state_id == before
    assert engine.budget.remaining >= 0
