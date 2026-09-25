"""R3.4.2 budget exhaustion must stop autonomous commits."""
from gnosis.core import Engine, State, TestResult, TransitionRecord
from gnosis.core.budget import Budget
from gnosis.self_learning.autonomous_cycle import run_one_endogenous_cycle

def seed_reflection_history(engine: Engine) -> None:
    for i in range(2):
        engine.history.append(
            TransitionRecord(
                from_state_id=engine.state.state_id,
                to_state_id=engine.state.state_id,
                candidate_id=f"seed:{i}",
                test_result=TestResult(False, ("meaningful change required",)),
                accepted=False,
                reason="rejected: meaningful change required",
                test_rule_id=engine.test_rule_id,
            )
        )

def test_budget_exhaustion_stops_next_cycle_without_commit():
    engine=Engine(state=State(elements={"a":1}), budget=Budget(total=1))
    seed_reflection_history(engine)
    first=run_one_endogenous_cycle(engine)
    assert first.transition is not None
    assert first.transition.accepted
    before=engine.state.state_id
    second=run_one_endogenous_cycle(engine)
    assert second.transition is None
    assert engine.state.state_id == before
    assert engine.budget.remaining == 0
