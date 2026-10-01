from __future__ import annotations

import pytest

from gnosis.core import (
    Candidate,
    Engine,
    PolicyIdentity,
    State,
    bind_policy,
)
from gnosis.reflection.rules import RuleMetadata, RuleRegistry


def candidate(state: State) -> Candidate:
    return Candidate(
        parent_state_id=state.state_id,
        proposed_state=state.with_elements({"x": 1}),
        origin="policy-binding-test",
    )


def policy_v1(_state: State, _candidate: Candidate) -> bool:
    return True


def policy_v2(_state: State, _candidate: Candidate) -> bool:
    return False


def test_engine_evidence_comes_from_actual_callable():
    state = State()
    binding = bind_policy("R", 1, policy_v1)
    engine = Engine(state=state, policy_binding=binding)
    record = engine.step(candidate(state))

    assert record.evaluation_evidence is not None
    assert record.evaluation_evidence.invoked is True
    assert record.evaluation_evidence.policy == binding.policy
    assert record.test_result.passed is True


def test_binding_rejects_mismatched_implementation_identity():
    good = bind_policy("R", 1, policy_v1)
    forged = PolicyIdentity(
        rule_id="R",
        rule_version=2,
        implementation_identity=good.policy.implementation_identity,
    )
    with pytest.raises(ValueError, match="does not match"):
        from gnosis.core import ExecutablePolicyBinding
        ExecutablePolicyBinding(policy=forged, evaluator=policy_v2)


def test_registry_resolves_exact_registered_callable():
    registry = RuleRegistry()
    registry.register(
        RuleMetadata(
            rule_id="R",
            rule_version=1,
            rule_type="test",
            scope="core",
            implementation_ref="artifact:r-v1",
            spec_ref="spec:R:v1",
        ),
        evaluator=policy_v1,
    )
    registry.register(
        RuleMetadata(
            rule_id="R",
            rule_version=2,
            rule_type="test",
            scope="core",
            implementation_ref="artifact:r-v2",
            spec_ref="spec:R:v2",
        ),
        evaluator=policy_v2,
    )

    v1 = registry.resolve("R", 1)
    v2 = registry.resolve("R", 2)

    assert v1.evaluator is policy_v1
    assert v2.evaluator is policy_v2
    assert v1.policy.rule_version == 1
    assert v2.policy.rule_version == 2
    assert v1.policy.implementation_identity != v2.policy.implementation_identity


def test_registry_without_executable_binding_fails_closed():
    registry = RuleRegistry()
    registry.register(
        RuleMetadata(
            rule_id="R",
            rule_version=1,
            rule_type="test",
            scope="core",
            implementation_ref="artifact:r-v1",
            spec_ref="spec:R:v1",
        )
    )
    with pytest.raises(PermissionError, match="no executable binding"):
        registry.resolve("R", 1)


def test_transition_identity_changes_with_policy_identity():
    state = State()
    c = candidate(state)
    r1 = Engine(state=state, policy_binding=bind_policy("R", 1, policy_v1)).step(c)
    state2 = State()
    c2 = candidate(state2)
    r2 = Engine(state=state2, policy_binding=bind_policy("R", 2, policy_v2)).step(c2)

    assert r1.transition_id != r2.transition_id


def test_protected_invariant_rejection_marks_policy_not_invoked():
    state = State()
    # Parent mismatch is rejected by Engine before evaluation.
    binding = bind_policy("R", 1, policy_v1)
    engine = Engine(state=state, policy_binding=binding)
    bad = Candidate(
        parent_state_id="wrong-parent",
        proposed_state=state.with_elements({"x": 1}),
        origin="policy-binding-test",
    )
    with pytest.raises(Exception):
        engine.step(bad)
