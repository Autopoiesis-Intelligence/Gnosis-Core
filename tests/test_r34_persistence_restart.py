"""R3.4.3 persistence/restart continuity proof."""
import sqlite3
from gnosis.core import Engine, State, TestResult, TransitionRecord, Candidate
from gnosis.core.budget import Budget
from gnosis.instances.instance import Instance, InstanceStatus
from gnosis.storage.database import initialize_database
from gnosis.storage.repositories import save_instance, recover_instance, _persist_transition
from gnosis.self_learning.autonomous_cycle import run_one_endogenous_cycle

def seed_reflection_history(engine):
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

def test_autonomous_cycle_survives_sqlite_restart():
    conn=sqlite3.connect(":memory:")
    initialize_database(conn)
    engine=Engine(state=State(elements={"a":1}), budget=Budget(total=2))
    seed_reflection_history(engine)
    instance=Instance("i","owner",engine,None,0,InstanceStatus.ACTIVE)
    save_instance(conn,instance,actor="owner")
    first=run_one_endogenous_cycle(engine)
    assert first.transition is not None
    _persist_transition(conn,instance,first.generation.candidates[0],first.transition,actor="owner")
    recovered=recover_instance(conn,"i")
    assert recovered.engine.state.state_id == first.transition.to_state_id
    assert recovered.engine.budget.spent == 1
    assert recovered.engine.budget.total == 2
    second=run_one_endogenous_cycle(recovered.engine)
    assert second.transition is not None
    _persist_transition(conn,recovered,second.generation.candidates[0],second.transition,actor="owner")
    final=recover_instance(conn,"i")
    assert final.engine.state.state_id == second.transition.to_state_id
    assert final.engine.budget.spent == 2
