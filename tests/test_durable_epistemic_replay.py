import pytest

from gnosis.storage.database import connect
from gnosis.storage.repositories import _append_epistemic_transition
from gnosis.world import EpistemicReplay, EpistemicState, TransitionAuthority


def test_durable_replay_reconstructs_from_sqlite():
    conn = connect(":memory:")
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
        basis_refs=("evidence:1",),
    )
    _append_epistemic_transition(conn, t1)
    _append_epistemic_transition(conn, t2)

    replay = EpistemicReplay.reconstruct_from_ledger(
        conn, "observation:1", EpistemicState.OBSERVED
    )
    assert replay.final_state is EpistemicState.ACCEPTED
    assert replay.applied_transition_ids == (t1.transition_id, t2.transition_id)


def test_durable_replay_does_not_accept_cross_subject_records():
    conn = connect(":memory:")
    t = TransitionAuthority.create(
        subject_ref="observation:2",
        from_state=EpistemicState.OBSERVED,
        to_state=EpistemicState.SUPPORTED,
        basis_refs=("evidence:1",),
    )
    _append_epistemic_transition(conn, t)
    replay = EpistemicReplay.reconstruct_from_ledger(
        conn, "observation:1", EpistemicState.OBSERVED
    )
    assert replay.final_state is EpistemicState.OBSERVED
    assert replay.applied_transition_ids == ()
