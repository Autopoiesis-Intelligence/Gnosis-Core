"""Regression: protected Core invariants cannot be bypassed by custom TestFn."""

from gnosis.core import Candidate, Engine, State


def test_custom_true_cannot_bypass_meaningful_change():
    current = State(elements={"a": 1}, version=1)
    proposed = State(elements={"a": 1}, version=2)
    candidate = Candidate(
        parent_state_id=current.state_id,
        proposed_state=proposed,
        origin="adversarial-custom-test",
    )

    engine = Engine(current, test_fn=lambda _current, _candidate: True)
    before = engine.state

    record = engine.step(candidate)

    assert record.accepted is False
    assert not record.test_result.passed
    assert any("meaningful_change" in reason for reason in record.test_result.reasons)
    assert engine.state == before
    assert engine.state.state_id == before.state_id


def test_custom_true_can_accept_genuine_change_after_protected_invariants():
    current = State(elements={"a": 1}, version=1)
    proposed = current.with_elements({"b": 2})
    candidate = Candidate(
        parent_state_id=current.state_id,
        proposed_state=proposed,
        origin="positive-custom-test",
    )

    engine = Engine(current, test_fn=lambda _current, _candidate: True)

    record = engine.step(candidate)

    assert record.accepted is True
    assert record.test_result.passed is True
    assert engine.state.state_id == proposed.state_id
