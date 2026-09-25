from gnosis.core.budget import Budget
from gnosis.core.evolution import Engine
from gnosis.core.types import State

def test_engine_state_is_read_only():
    engine = Engine(state=State(), budget=Budget(total=1))
    try:
        engine.state = State(elements={"bypass": True})
    except AttributeError:
        return
    raise AssertionError("Engine.state must reject direct assignment")
