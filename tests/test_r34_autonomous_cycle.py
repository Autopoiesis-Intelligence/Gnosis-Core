from gnosis.core import Engine, State
from gnosis.self_learning.autonomous_cycle import run_one_endogenous_cycle

def test_one_endogenous_cycle_uses_reflection_and_core_select():
    engine=Engine(state=State(elements={"a":1}))
    # Seed repeated canonical rejections so reflection has evidence-backed proposals.
    engine.history.clear()
    for i in range(2):
        engine.history.append(engine.step(
            __import__("gnosis.core",fromlist=["Candidate"]).Candidate(
                parent_state_id=engine.state.state_id,
                proposed_state=State(elements=dict(engine.state.elements),version=engine.state.version+1),
                origin=f"seed:{i}",
            )
        ))
    before=engine.state.state_id
    result=run_one_endogenous_cycle(engine)
    assert result.generation.bounded
    assert result.generation.candidates
    assert result.transition is not None
    assert result.transition.accepted
    assert engine.state.state_id != before
    assert result.transition.candidate_id in {c.candidate_id for c in result.generation.candidates}
