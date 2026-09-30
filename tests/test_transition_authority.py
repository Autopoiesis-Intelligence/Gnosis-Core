import pytest

from gnosis.world import EpistemicState, TransitionAuthority


def test_transition_authority_creates_only_policy_valid_transitions():
    transition = TransitionAuthority.create(
        subject_ref="observation:1",
        from_state=EpistemicState.SUPPORTED,
        to_state=EpistemicState.ACCEPTED,
        basis_refs=("evidence:1",),
    )
    assert transition.from_state == "SUPPORTED"
    assert transition.to_state == "ACCEPTED"


def test_transition_authority_rejects_direct_acceptance():
    with pytest.raises(ValueError):
        TransitionAuthority.create(
            subject_ref="observation:1",
            from_state=EpistemicState.OBSERVED,
            to_state=EpistemicState.ACCEPTED,
        )


def test_transition_authority_rejects_acceptance_without_basis():
    with pytest.raises(ValueError, match="basis_refs"):
        TransitionAuthority.create(
            subject_ref="observation:1",
            from_state=EpistemicState.SUPPORTED,
            to_state=EpistemicState.ACCEPTED,
        )
