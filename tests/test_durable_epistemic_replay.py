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


def test_durable_replay_uses_ledger_position_not_timestamp():
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
        basis_refs=("evidence:2",),
    )
    _append_epistemic_transition(conn, t1, created_at="2026-01-01T00:00:01Z")
    _append_epistemic_transition(conn, t2, created_at="2025-01-01T00:00:01Z")
    rows = conn.execute(
        "SELECT ledger_position, transition_id FROM epistemic_transitions ORDER BY ledger_position"
    ).fetchall()
    assert rows == [(1, t1.transition_id), (2, t2.transition_id)]
    replay = EpistemicReplay.reconstruct_from_ledger(
        conn, "observation:1", EpistemicState.OBSERVED
    )
    assert replay.final_state is EpistemicState.ACCEPTED
