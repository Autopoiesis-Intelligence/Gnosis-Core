from gnosis.core.budget import Budget
from gnosis.core.evolution import Engine
from gnosis.core.types import State

def test_engine_history_is_read_only():
    engine = Engine(state=State(), budget=Budget(total=1))
    try:
        engine.history.append("direct")
    except AttributeError:
        return
    raise AssertionError("Engine.history must reject direct mutation")
