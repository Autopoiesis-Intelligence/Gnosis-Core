from __future__ import annotations

import pytest

from gnosis.core import (
    Candidate,
    Engine,
    PolicyIdentity,
    State,
    bind_policy,
)
from gnosis.reflection.rules import RuleMetadata, AuthorizedRuleRegistry, _REGISTRY_AUTHORITY


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
    registry = AuthorizedRuleRegistry(_authority=_REGISTRY_AUTHORITY)
    registry._register_authorized(RuleMetadata("R", 1, "test", "core", "artifact:r-v1", "spec:R:v1"), evaluator=policy_v1)
    binding = registry.resolve("R", 1)
    engine = Engine(state=state, policy_binding=binding)
    record = engine.step(candidate(state))

    assert record.evaluation_evidence is not None
    assert record.evaluation_evidence.invoked is True
    assert record.evaluation_evidence.policy == binding.policy
    assert record.test_result.passed is True


def test_binding_rejects_mismatched_implementation_identity():
    registry = AuthorizedRuleRegistry(_authority=_REGISTRY_AUTHORITY)
    registry._register_authorized(RuleMetadata("R", 1, "test", "core", "artifact:r-v1", "spec:R:v1"), evaluator=policy_v1)
    good = registry.resolve("R", 1)
    forged = PolicyIdentity(
        rule_id="R",
        rule_version=2,
        implementation_identity=good.policy.implementation_identity,
    )
    with pytest.raises(ValueError, match="does not match"):
        from gnosis.core import ExecutablePolicyBinding
        ExecutablePolicyBinding(policy=forged, evaluator=policy_v2)


def test_registry_resolves_exact_registered_callable():
    registry = AuthorizedRuleRegistry(_authority=_REGISTRY_AUTHORITY)
    registry._register_authorized(
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
    registry._register_authorized(
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
    registry = AuthorizedRuleRegistry(_authority=_REGISTRY_AUTHORITY)
    registry._register_authorized(
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
    reg1 = AuthorizedRuleRegistry(_authority=_REGISTRY_AUTHORITY); reg1._register_authorized(RuleMetadata("R", 1, "test", "core", "artifact:r-v1", "spec:R:v1"), evaluator=policy_v1)
    r1 = Engine(state=state, policy_binding=reg1.resolve("R", 1)).step(c)
    state2 = State()
    c2 = candidate(state2)
    reg2 = AuthorizedRuleRegistry(_authority=_REGISTRY_AUTHORITY); reg2._register_authorized(RuleMetadata("R", 2, "test", "core", "artifact:r-v2", "spec:R:v2"), evaluator=policy_v2)
    r2 = Engine(state=state2, policy_binding=reg2.resolve("R", 2)).step(c2)

    assert r1.transition_id != r2.transition_id


def test_protected_invariant_rejection_marks_policy_not_invoked():
    state = State()
    registry = AuthorizedRuleRegistry(_authority=_REGISTRY_AUTHORITY); registry._register_authorized(RuleMetadata("R", 1, "test", "core", "artifact:r-v1", "spec:R:v1"), evaluator=policy_v1)
    binding = registry.resolve("R", 1)
    engine = Engine(state=state, policy_binding=binding)
    bad = Candidate(
        parent_state_id=state.state_id,
        proposed_state=state,
        origin="policy-binding-test",
    )
    record = engine.step(bad)
    assert record.accepted is False
    assert record.evaluation_evidence is not None
    assert record.evaluation_evidence.invoked is False


def test_sqlite_round_trip_preserves_policy_identity(sqlite_conn):
    from gnosis.instances.instance import Instance
    from gnosis.storage import save_instance, load_instance

    state = State()
    registry = AuthorizedRuleRegistry(_authority=_REGISTRY_AUTHORITY)
    registry._register_authorized(RuleMetadata("R", 1, "test", "core", "artifact:r-v1", "spec:R:v1"), evaluator=policy_v1)
    binding = registry.resolve("R", 1)
    instance = Instance.create_root("u", state)
    instance.engine.policy_binding = binding
    instance.engine.test_fn = binding.evaluator
    instance.engine.test_rule_id = binding.policy.rule_id
    save_instance(sqlite_conn, instance)

    registry = AuthorizedRuleRegistry(_authority=_REGISTRY_AUTHORITY)
    registry._register_authorized(
        RuleMetadata("R", 1, "test", "core", "artifact:r-v1", "spec:R:v1"),
        evaluator=policy_v1,
    )
    restored = load_instance(sqlite_conn, instance.instance_id, policy_registry=registry)
    assert restored.engine.policy_binding is not None
    assert restored.engine.policy_binding.policy == binding.policy
    assert restored.engine.policy_binding.evaluator is policy_v1


def test_custom_policy_recovery_fails_closed_without_registry(sqlite_conn):
    from gnosis.instances.instance import Instance
    from gnosis.storage import save_instance, load_instance

    instance = Instance.create_root("u", State())
    registry = AuthorizedRuleRegistry(_authority=_REGISTRY_AUTHORITY)
    registry._register_authorized(RuleMetadata("R", 1, "test", "core", "artifact:r-v1", "spec:R:v1"), evaluator=policy_v1)
    binding = registry.resolve("R", 1)
    instance.engine.policy_binding = binding
    instance.engine.test_fn = binding.evaluator
    instance.engine.test_rule_id = binding.policy.rule_id
    save_instance(sqlite_conn, instance)

    with pytest.raises(Exception, match="policy registry"):
        load_instance(sqlite_conn, instance.instance_id)


def test_caller_cannot_issue_trusted_binding():
    with pytest.raises(PermissionError, match="RuleRegistry"):
        bind_policy("forged", 1, policy_v1)


def test_legacy_raw_callable_cannot_enter_durable_instance_chain(sqlite_conn):
    from gnosis.instances.instance import Instance
    from gnosis.storage import save_instance

    instance = Instance(
        instance_id="legacy-raw-policy",
        owner_id="u",
        engine=Engine(state=State(), test_fn=policy_v1, test_rule_id="R"),
    )
    with pytest.raises(Exception, match="no executable policy binding"):
        save_instance(sqlite_conn, instance)

def test_caller_cannot_forge_binding_authority():
    from gnosis.core import ExecutablePolicyBinding

    registry = AuthorizedRuleRegistry(_authority=_REGISTRY_AUTHORITY)
    registry._register_authorized(
        RuleMetadata("R", 1, "test", "core", "artifact:r-v1", "spec:R:v1"),
        evaluator=policy_v1,
    )
    trusted = registry.resolve("R", 1)
    forged = PolicyIdentity(
        rule_id=trusted.policy.rule_id,
        rule_version=trusted.policy.rule_version,
        implementation_identity=trusted.policy.implementation_identity,
    )
    with pytest.raises(PermissionError, match="trusted authority"):
        ExecutablePolicyBinding(policy=forged, evaluator=policy_v1, _authority=object())


def test_registry_issued_binding_accepts_exact_identity():
    from gnosis.core import implementation_identity

    registry = AuthorizedRuleRegistry(_authority=_REGISTRY_AUTHORITY)
    registry._register_authorized(
        RuleMetadata("R", 1, "test", "core", "artifact:r-v1", "spec:R:v1"),
        evaluator=policy_v1,
    )
    binding = registry.resolve("R", 1)
    assert binding.policy.implementation_identity == implementation_identity(binding.evaluator)
