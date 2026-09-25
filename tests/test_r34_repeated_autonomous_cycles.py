"""R3.4.2 repeated bounded endogenous cycles."""
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

def test_repeated_endogenous_cycles_preserve_progress_and_bound():
    engine=Engine(state=State(elements={"a":1}), budget=Budget(total=3))
    seed_reflection_history(engine)
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
