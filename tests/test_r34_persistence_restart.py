"""R3.4.3 persistence/restart continuity proof."""
from gnosis.core import Engine, State, TestResult, TransitionRecord, Candidate
from gnosis.core.budget import Budget
from gnosis.instances.instance import Instance, InstanceStatus
from gnosis.storage.repositories import save_instance, recover_instance, _persist_transition
from gnosis.storage.database import connect
from gnosis.self_learning.autonomous_cycle import run_one_endogenous_cycle

def seed_reflection_history(conn, instance):
    state = instance.engine.state
    for i in range(2):
        candidate = Candidate(
            parent_state_id=state.state_id,
            proposed_state=State(elements=dict(state.elements), version=state.version),
            origin=f"seed:{i}",
        )
        record = TransitionRecord(
            from_state_id=state.state_id,
            to_state_id=state.state_id,
            candidate_id=candidate.candidate_id,
            test_result=TestResult(False, ("meaningful change required",)),
            accepted=False,
            reason="rejected: meaningful change required",
            test_rule_id=instance.engine.test_rule_id,
        )
        _persist_transition(conn, instance, candidate, record, actor="owner")

def test_autonomous_cycle_survives_sqlite_restart():
    conn=connect(":memory:")
    engine=Engine(state=State(elements={"a":1}), budget=Budget(total=2))
    instance=Instance("i","owner",engine,None,0,InstanceStatus.ACTIVE)
    save_instance(conn,instance,actor="owner")
    seed_reflection_history(conn,instance)

    recovered=recover_instance(conn,"i")
    assert len(recovered.engine.history) == 2
    assert recovered.engine.state.state_id == instance.engine.state.state_id
    assert conn.execute("SELECT current_state_id FROM instances WHERE instance_id='i'").fetchone()[0] == recovered.engine.state.state_id

    first=run_one_endogenous_cycle(recovered.engine)
    assert first.transition is not None
    assert first.transition.from_state_id == recovered.engine.history[-2].from_state_id
    assert first.transition.from_state_id == recovered.engine.state.state_id or first.transition.from_state_id != first.transition.to_state_id
    _persist_transition(conn,recovered,first.generation.candidates[0],first.transition,actor="owner")

    recovered2=recover_instance(conn,"i")
    assert recovered2.engine.state.state_id == first.transition.to_state_id
    assert recovered2.engine.budget.spent == 1
    assert recovered2.engine.budget.total == 2
    assert len(recovered2.engine.history) == 3

    second=run_one_endogenous_cycle(recovered2.engine)
    assert second.transition is not None
    _persist_transition(conn,recovered2,second.generation.candidates[0],second.transition,actor="owner")

    final=recover_instance(conn,"i")
    assert final.engine.state.state_id == second.transition.to_state_id
    assert final.engine.budget.spent == 2
    assert len(final.engine.history) == 4
