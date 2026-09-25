import pytest

from gnosis.self_learning.evidence_loop import (
    creates_execution_authority,
    influences_next_cycle,
    is_no_op,
    preserves_causal_binding,
    record_cycle_evidence,
)


def make(**overrides):
    values = {
        "cycle_id": "cycle:2",
        "parent_cycle_id": "cycle:1",
        "input_digest": "sha256:input",
        "initial_state_digest": "sha256:old",
        "candidate_id": "candidate:2",
        "execution_id": "exec:2",
        "verification_id": "verify:2",
        "outcome": "ACCEPTED",
        "resulting_state_digest": "sha256:new",
        "commit_id": "commit:2",
        "learning_id": "learning:2",
        "evidence_refs": ("e1", "e2"),
    }
    values.update(overrides)
    return record_cycle_evidence(**values)


def test_evidence_is_deterministic():
    assert make() == make()


def test_causal_binding_is_exact():
    evidence = make()
    assert preserves_causal_binding(
        evidence=evidence, cycle_id="cycle:2", initial_state_digest="sha256:old"
    )
    assert not preserves_causal_binding(
        evidence=evidence, cycle_id="cycle:wrong", initial_state_digest="sha256:old"
    )


def test_accepted_requires_commit():
    with pytest.raises(ValueError):
        make(commit_id=None)


def test_rejected_cannot_have_commit():
    with pytest.raises(ValueError):
        make(outcome="REJECTED", commit_id="commit:2")


def test_rejected_can_feed_learning():
    evidence = make(outcome="REJECTED", commit_id=None)
    assert influences_next_cycle(evidence=evidence)


def test_no_op_is_detected():
    evidence = make(resulting_state_digest="sha256:old")
    assert is_no_op(evidence=evidence)


def test_learning_influence_requires_learning_id():
    evidence = make(learning_id=None)
    assert not influences_next_cycle(evidence=evidence)


def test_evidence_never_grants_authority():
    assert not creates_execution_authority(evidence=make())


def test_missing_evidence_is_rejected():
    with pytest.raises(ValueError):
        make(evidence_refs=())
