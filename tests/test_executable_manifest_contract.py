from dataclasses import FrozenInstanceError

import pytest

from gnosis.core.policy import (
    ImmutableExecutableManifest,
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
        parent_state_digest=parent.content_id,
        policy=policy,
    )
    second = executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=parent.content_id,
        policy=policy,
    )

    assert first == second
    assert first.startswith("sha256:")


def test_manifest_digest_changes_when_policy_implementation_changes():
    parent, candidate = _candidate()
    first = executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=parent.content_id,
        policy=PolicyIdentity("test-rule", 1, "python-source-sha256:impl-a"),
    )
    second = executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=parent.content_id,
        policy=PolicyIdentity("test-rule", 1, "python-source-sha256:impl-b"),
    )

    assert first != second


def test_manifest_digest_changes_when_rule_version_changes():
    parent, candidate = _candidate()
    first = executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=parent.content_id,
        policy=PolicyIdentity("test-rule", 1, "python-source-sha256:impl-a"),
    )
    second = executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=parent.content_id,
        policy=PolicyIdentity("test-rule", 2, "python-source-sha256:impl-a"),
    )

    assert first != second


def test_manifest_digest_changes_when_candidate_binding_changes():
    parent, candidate = _candidate()
    policy = PolicyIdentity("test-rule", 1, "python-source-sha256:impl-a")
    first = executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=parent.content_id,
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
        parent_state_digest=parent.content_id,
        policy=policy,
    )

    assert first != second


def test_manifest_digest_changes_when_parent_state_changes():
    parent, candidate = _candidate()
    policy = PolicyIdentity("test-rule", 1, "python-source-sha256:impl-a")
    first = executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=parent.content_id,
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
        parent_state_digest=other_parent.content_id,
        policy=policy,
    )

    assert first != second


def test_immutable_manifest_is_frozen_and_canonical():
    parent, candidate = _candidate()
    manifest = ImmutableExecutableManifest(
        candidate_binding_digest=candidate.binding_digest(parent.content_id),
        parent_state_digest=parent.content_id,
        rule_id="test-rule",
        rule_version=1,
        implementation_identity="python-source-sha256:impl-a",
    )

    assert manifest.canonical_payload() == {
        "candidate_binding_digest": candidate.binding_digest(parent.content_id),
        "parent_state_digest": parent.content_id,
        "policy": {
            "implementation_identity": "python-source-sha256:impl-a",
            "rule_id": "test-rule",
            "rule_version": 1,
        },
    }
    assert manifest.manifest_digest == executable_binding_manifest_digest(
        candidate=candidate,
        parent_state_digest=parent.content_id,
        policy=PolicyIdentity("test-rule", 1, "python-source-sha256:impl-a"),
    )
    with pytest.raises(FrozenInstanceError):
        manifest.rule_version = 2


def test_manifest_rejects_callable_as_implementation_identity():
    parent, candidate = _candidate()
    with pytest.raises((TypeError, ValueError)):
        ImmutableExecutableManifest(
            candidate_binding_digest=candidate.binding_digest(parent.content_id),
            parent_state_digest=parent.content_id,
            rule_id="test-rule",
            rule_version=1,
            implementation_identity=lambda *_: True,
        )


def test_manifest_digest_changes_when_parent_digest_changes_directly():
    manifest = ImmutableExecutableManifest(
        candidate_binding_digest="sha256:candidate",
        parent_state_digest="sha256:parent-a",
        rule_id="test-rule",
        rule_version=1,
        implementation_identity="python-source-sha256:impl-a",
    )
    altered = ImmutableExecutableManifest(
        candidate_binding_digest="sha256:candidate",
        parent_state_digest="sha256:parent-b",
        rule_id="test-rule",
        rule_version=1,
        implementation_identity="python-source-sha256:impl-a",
    )
    assert manifest.manifest_digest != altered.manifest_digest


def test_manifest_digest_changes_when_rule_id_changes():
    common = dict(
        candidate_binding_digest="sha256:candidate",
        parent_state_digest="sha256:parent",
        rule_version=1,
        implementation_identity="python-source-sha256:impl-a",
    )
    assert ImmutableExecutableManifest(rule_id="rule-a", **common).manifest_digest != ImmutableExecutableManifest(rule_id="rule-b", **common).manifest_digest
