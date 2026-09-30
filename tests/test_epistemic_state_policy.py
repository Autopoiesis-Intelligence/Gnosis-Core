import pytest

from gnosis.world import EpistemicState, TransitionPolicy


def test_transition_policy_is_deterministic():
    assert TransitionPolicy.allows(EpistemicState.OBSERVED, EpistemicState.SUPPORTED)
    assert not TransitionPolicy.allows(EpistemicState.OBSERVED, EpistemicState.ACCEPTED)
    assert TransitionPolicy.allows(EpistemicState.ACCEPTED, EpistemicState.SUPERSEDED)


def test_accepted_requires_basis():
    with pytest.raises(ValueError, match="basis_refs"):
        TransitionPolicy.validate(
            EpistemicState.SUPPORTED,
            EpistemicState.ACCEPTED,
        )
    TransitionPolicy.validate(
        EpistemicState.SUPPORTED,
        EpistemicState.ACCEPTED,
        basis_refs=("evidence:1",),
    )


def test_terminal_states_cannot_transition():
    assert not TransitionPolicy.allows(EpistemicState.REJECTED, EpistemicState.ACCEPTED)
    assert not TransitionPolicy.allows(EpistemicState.SUPERSEDED, EpistemicState.ACCEPTED)
