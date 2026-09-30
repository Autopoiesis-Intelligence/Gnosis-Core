import pytest

from gnosis.world import EpistemicTransition


def test_epistemic_transition_is_content_identified():
    transition = EpistemicTransition(
        subject_ref="observation:1",
        from_state="OBSERVED",
        to_state="SUPPORTED",
        basis_refs=("evidence:1",),
        reason_ref="finding:1",
    )
    assert transition.transition_id


def test_epistemic_transition_is_immutable():
    transition = EpistemicTransition(
        subject_ref="observation:1",
        from_state="OBSERVED",
        to_state="SUPPORTED",
        basis_refs=("evidence:1",),
    )
    with pytest.raises(AttributeError):
        transition.to_state = "ACCEPTED"


def test_epistemic_transition_does_not_mutate_subject_or_assert_truth():
    transition = EpistemicTransition(
        subject_ref="observation:1",
        from_state="OBSERVED",
        to_state="ACCEPTED",
    )
    assert transition.subject_ref == "observation:1"
    assert not hasattr(transition, "evidence")
    assert not hasattr(transition, "verified")
