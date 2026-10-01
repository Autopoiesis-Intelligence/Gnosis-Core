from gnosis.core.policy import (
    PolicyIdentity,
    executable_binding_manifest_digest,
)
from gnosis.core.types import Candidate, State
from gnosis.reflection.rules import default_rule_registry


def _candidate() -> Candidate:
    parent = State(elements={"a": 1})
    return Candidate(
        parent_state_id=parent.state_id,
        proposed_state=parent.with_elements({"b": 2}),
        origin="r12-test",
        seed=7,
    )


def _policy(identity: str = "python-source-sha256:policy-a") -> PolicyIdentity:
    return PolicyIdentity(
        rule_id="test-rule:diagnostic-policy",
        rule_version=1,
        implementation_identity=identity,
    )


def test_manifest_digest_binds_existing_candidate_binding_to_policy_identity():
    candidate = _candidate()
    digest = executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=candidate.parent_state_id,
        policy=_policy(),
    )
    assert digest.startswith("sha256:")
    assert digest != candidate.binding_digest(candidate.parent_state_id)


def test_manifest_digest_changes_when_implementation_identity_changes():
    candidate = _candidate()
    a = executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=candidate.parent_state_id,
        policy=_policy("python-source-sha256:policy-a"),
    )
    b = executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=candidate.parent_state_id,
        policy=_policy("python-source-sha256:policy-b"),
    )
    assert a != b


def test_manifest_digest_is_deterministic_for_same_binding():
    candidate = _candidate()
    policy = _policy()
    a = executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=candidate.parent_state_id,
        policy=policy,
    )
    b = executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=candidate.parent_state_id,
        policy=policy,
    )
    assert a == b


def test_manifest_digest_does_not_change_legacy_candidate_binding_digest():
    candidate = _candidate()
    before = candidate.binding_digest(candidate.parent_state_id)
    executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=candidate.parent_state_id,
        policy=_policy(),
    )
    assert candidate.binding_digest(candidate.parent_state_id) == before


def test_manifest_digest_accepts_identity_from_authorized_registry_binding():
    candidate = _candidate()
    binding = default_rule_registry().resolve("test-rule:default", 1)
    digest = executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=candidate.parent_state_id,
        policy=binding.policy,
    )
    assert binding.policy.implementation_identity
    assert digest.startswith("sha256:")
