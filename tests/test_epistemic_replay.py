import pytest

from gnosis.world import (
    EpistemicReplay,
    EpistemicState,
    TransitionAuthority,
)


def test_replay_reconstructs_epistemic_chain():
    t1 = TransitionAuthority.create(
        subject_ref="observation:1",
        from_state=EpistemicState.OBSERVED,
        to_state=EpistemicState.SUPPORTED,
        basis_refs=("evidence:1",),
    )
    t2 = TransitionAuthority.create(
        subject_ref="observation:1",
        from_state=EpistemicState.SUPPORTED,
        to_state=EpistemicState.ACCEPTED,
        basis_refs=("evidence:1", "evidence:2"),
    )
    replay = EpistemicReplay.reconstruct(
        "observation:1",
        EpistemicState.OBSERVED,
        (t1, t2),
    )
    assert replay.final_state is EpistemicState.ACCEPTED
    assert replay.applied_transition_ids == (t1.transition_id, t2.transition_id)


def test_replay_rejects_broken_continuity():
    t = TransitionAuthority.create(
        subject_ref="observation:1",
        from_state=EpistemicState.SUPPORTED,
        to_state=EpistemicState.ACCEPTED,
        basis_refs=("evidence:1",),
    )
    with pytest.raises(ValueError, match="continuity"):
        EpistemicReplay.reconstruct(
            "observation:1",
            EpistemicState.OBSERVED,
            (t,),
        )


def test_replay_rejects_cross_subject_transition():
    t = TransitionAuthority.create(
        subject_ref="observation:2",
        from_state=EpistemicState.OBSERVED,
        to_state=EpistemicState.SUPPORTED,
        basis_refs=("evidence:1",),
    )
    with pytest.raises(ValueError, match="subject"):
        EpistemicReplay.reconstruct(
            "observation:1",
            EpistemicState.OBSERVED,
            (t,),
        )
