from gnosis.core.evolution import Engine
from gnosis.core.types import Candidate, State


def test_engine_default_execution_uses_authorized_policy_binding():
    parent = State(elements={"x": 1})
    candidate = Candidate(
        parent_state_id=parent.state_id,
        proposed_state=parent.with_elements({"y": 2}),
        origin="r12-e2e",
        seed=1,
    )
    engine = Engine(state=parent)

    record = engine.step(candidate)

    assert engine.policy_binding is not None
    assert engine.policy_binding.policy.rule_id == "test-rule:default"
    assert record.evaluation_evidence is not None
    assert record.evaluation_evidence.policy == engine.policy_binding.policy
    assert record.evaluation_evidence.invoked is True
