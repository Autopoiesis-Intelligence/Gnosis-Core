import sqlite3
import pytest

from gnosis.storage.repositories import (
    StorageCorruptionError,
    load_epistemic_transition,
    _append_epistemic_transition,
    save_world_observation,
    load_world_observation,
)
from gnosis.storage.database import connect
from gnosis.world import EpistemicState, TransitionAuthority, WorldObservation


def test_world_model_observation_and_transition_round_trip():
    conn = connect(":memory:")
    observation = WorldObservation(
        context_ref="zone",
        distinction="temperature",
        properties={"value": 20, "unit": "C"},
    )
    save_world_observation(conn, observation)
    transition = TransitionAuthority.create(
        subject_ref=observation.observation_id,
        from_state=EpistemicState.OBSERVED,
        to_state=EpistemicState.SUPPORTED,
        basis_refs=("evidence:1",),
    )
    _append_epistemic_transition(conn, transition)
    assert load_world_observation(conn, observation.observation_id) == observation
    assert load_epistemic_transition(conn, transition.transition_id) == transition
    audit = conn.execute("SELECT action,resource,result,transition_id FROM audit_events WHERE transition_id=?", (transition.transition_id,)).fetchall()
    assert audit == [("epistemic_transition.append", observation.observation_id, "accepted", transition.transition_id)]


def test_epistemic_transition_storage_is_append_only_and_tamper_evident():
    conn = connect(":memory:")
    transition = TransitionAuthority.create(
        subject_ref="observation:1",
        from_state=EpistemicState.OBSERVED,
        to_state=EpistemicState.SUPPORTED,
        basis_refs=("evidence:1",),
    )
    _append_epistemic_transition(conn, transition)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM epistemic_transitions WHERE transition_id=?", (transition.transition_id,))
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE epistemic_transitions SET to_state='ACCEPTED' WHERE transition_id=?", (transition.transition_id,))


def test_unsealed_epistemic_transition_cannot_enter_persistence():
    conn = connect(":memory:")
    from gnosis.world import EpistemicTransition
    transition = EpistemicTransition(
        subject_ref="observation:1",
        from_state="OBSERVED",
        to_state="SUPPORTED",
        basis_refs=("evidence:1",),
    )
    with pytest.raises(PermissionError, match="TransitionAuthority"):
        _append_epistemic_transition(conn, transition)


def test_epistemic_transition_audit_is_idempotent_on_replay():
    conn = connect(":memory:")
    transition = TransitionAuthority.create(
        subject_ref="observation:1",
        from_state=EpistemicState.OBSERVED,
        to_state=EpistemicState.SUPPORTED,
        basis_refs=("evidence:1",),
    )
    _append_epistemic_transition(conn, transition)
    _append_epistemic_transition(conn, transition)
    assert conn.execute("SELECT COUNT(*) FROM epistemic_transitions").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM audit_events WHERE transition_id=?", (transition.transition_id,)).fetchone()[0] == 1


def test_duplicate_transition_is_idempotent_but_tampered_duplicate_is_rejected():
    conn = connect(":memory:")
    transition = TransitionAuthority.create(
        subject_ref="observation:1",
        from_state=EpistemicState.OBSERVED,
        to_state=EpistemicState.SUPPORTED,
        basis_refs=("evidence:1",),
    )
    _append_epistemic_transition(conn, transition)
    _append_epistemic_transition(conn, transition)
    assert conn.execute("SELECT COUNT(*) FROM epistemic_transitions").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM audit_events").fetchone()[0] == 1

    with pytest.raises(PermissionError):
        from gnosis.world import EpistemicTransition
        forged = EpistemicTransition(
            subject_ref="observation:1",
            from_state="OBSERVED",
            to_state="ACCEPTED",
            basis_refs=("evidence:1",),
        )
        _append_epistemic_transition(conn, forged)


def test_rollback_removes_transition_and_audit_together():
    conn = connect(":memory:")
    transition = TransitionAuthority.create(
        subject_ref="observation:rollback",
        from_state=EpistemicState.OBSERVED,
        to_state=EpistemicState.SUPPORTED,
        basis_refs=("evidence:rollback",),
    )
    original_commit = conn.commit
    def fail_commit():
        raise RuntimeError("forced commit failure")
    conn.commit = fail_commit
    with pytest.raises(RuntimeError, match="forced commit failure"):
        _append_epistemic_transition(conn, transition)
    conn.commit = original_commit
    assert conn.execute("SELECT COUNT(*) FROM epistemic_transitions").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM audit_events").fetchone()[0] == 0
