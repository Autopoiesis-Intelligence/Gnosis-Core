import pytest

from gnosis.reflection.rules import RuleMetadata, RuleRegistry, _REGISTRY_AUTHORITY


def _rule(version: int) -> RuleMetadata:
    return RuleMetadata(
        rule_id="test-rule:diagnostic-policy",
        rule_version=version,
        rule_type="test_policy",
        scope="diagnostic-corpus",
        implementation_ref="gnosis.core.engine:Engine.test_fn",
        spec_ref="docs/CORE_REFLECTION_R1_TASK.md",
        invariant_refs=("transition-validity",),
    )


def test_registry_enforces_unique_rule_versions_and_exposes_latest():
    registry = RuleRegistry()
    registry.register(_rule(1))
    registry.register(_rule(2))

    assert registry.versions("test-rule:diagnostic-policy") == (1, 2)
    assert registry.latest("test-rule:diagnostic-policy").rule_version == 2
    assert registry.get("test-rule:diagnostic-policy", 1).rule_version == 1

    with pytest.raises(ValueError):
        registry.register(_rule(2))


def test_registry_rejects_invalid_versions_and_unknown_rules():
    registry = RuleRegistry()
    with pytest.raises(ValueError):
        registry.register(_rule(0))
    with pytest.raises(KeyError):
        registry.get("missing-rule", 1)
    with pytest.raises(KeyError):
        registry.latest("missing-rule")


def test_registry_is_descriptive_and_has_no_activation_api():
    registry = RuleRegistry()
    registry.register(_rule(1))
    assert not hasattr(registry, "activate")
    assert registry.snapshot() == (_rule(1),)


def test_metadata_registry_cannot_issue_executable_binding():
    registry = RuleRegistry()
    registry.register(_rule(1))
    assert not hasattr(registry, "resolve")


def test_authorized_registry_issues_exact_executable_binding():
    from gnosis.reflection.rules import AuthorizedRuleRegistry

    registry = AuthorizedRuleRegistry(_authority=_REGISTRY_AUTHORITY)
    evaluator = lambda _state, _candidate: True
    registry.register(_rule(1), evaluator=evaluator)
    binding = registry.resolve("test-rule:diagnostic-policy", 1)
    assert binding.evaluator is evaluator


def test_authorized_registry_rejects_caller_construction_without_authority():
    from gnosis.reflection.rules import AuthorizedRuleRegistry

    with pytest.raises(PermissionError, match="Core authority"):
        AuthorizedRuleRegistry()
    with pytest.raises(PermissionError, match="Core authority"):
        AuthorizedRuleRegistry(_authority=object())


def test_default_rule_registry_is_core_authorized_and_resolves_default():
    from gnosis.reflection.rules import default_rule_registry

    registry = default_rule_registry()
    binding = registry.resolve("test-rule:default", 1)
    assert binding.policy.rule_id == "test-rule:default"
    assert binding.policy.rule_version == 1
