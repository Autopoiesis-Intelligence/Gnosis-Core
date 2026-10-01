from gnosis.core.policy import (
    PolicyIdentity,
    executable_binding_manifest_digest,
)
from gnosis.core.types import Candidate, State


def _candidate():
    parent = State(elements={"x": 1})
    return parent, Candidate(
        parent_state_id=parent.state_id,
        proposed_state=parent.with_elements({"x": 2}),
        origin="manifest-contract",
        seed=1,
    )


def test_manifest_digest_is_deterministic_for_same_execution_contract():
    parent, candidate = _candidate()
    policy = PolicyIdentity("test-rule", 1, "python-source-sha256:impl-a")

    first = executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=parent.state_id,
        policy=policy,
    )
    second = executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=parent.state_id,
        policy=policy,
    )

    assert first == second
    assert first.startswith("sha256:")


def test_manifest_digest_changes_when_policy_implementation_changes():
    parent, candidate = _candidate()
    first = executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=parent.state_id,
        policy=PolicyIdentity("test-rule", 1, "python-source-sha256:impl-a"),
    )
    second = executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=parent.state_id,
        policy=PolicyIdentity("test-rule", 1, "python-source-sha256:impl-b"),
    )

    assert first != second


def test_manifest_digest_changes_when_rule_version_changes():
    parent, candidate = _candidate()
    first = executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=parent.state_id,
        policy=PolicyIdentity("test-rule", 1, "python-source-sha256:impl-a"),
    )
    second = executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=parent.state_id,
        policy=PolicyIdentity("test-rule", 2, "python-source-sha256:impl-a"),
    )

    assert first != second


def test_manifest_digest_changes_when_candidate_binding_changes():
    parent, candidate = _candidate()
    policy = PolicyIdentity("test-rule", 1, "python-source-sha256:impl-a")
    first = executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=parent.state_id,
        policy=policy,
    )
    altered = Candidate(
        parent_state_id=parent.state_id,
        proposed_state=parent.with_elements({"x": 3}),
        origin="manifest-contract",
        seed=1,
    )
    second = executable_binding_manifest_digest(
        candidate=altered,
        parent_state_digest=parent.state_id,
        policy=policy,
    )

    assert first != second


def test_manifest_digest_changes_when_parent_state_changes():
    parent, candidate = _candidate()
    policy = PolicyIdentity("test-rule", 1, "python-source-sha256:impl-a")
    first = executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=parent.state_id,
        policy=policy,
    )
    other_parent = State(elements={"x": 9})
    other_candidate = Candidate(
        parent_state_id=other_parent.state_id,
        proposed_state=other_parent.with_elements({"x": 2}),
        origin="manifest-contract",
        seed=1,
    )
    second = executable_binding_manifest_digest(
        candidate=other_candidate,
        parent_state_digest=other_parent.state_id,
        policy=policy,
    )

    assert first != second
